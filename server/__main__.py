import argparse
import asyncio
import json
import re
from typing import Callable, Optional

from websockets.exceptions import ConnectionClosedError
from websockets.server import WebSocketServerProtocol, serve

from .error import Error, InvalidUsernameError, NameInUseError, encode_error
from .message import IdentifyMessage, Message, MessageFactory, SendMessage
from .reply import Reply, ReplyFactory
from .types import JSONObject


class Client:
    # lowercase names that can have dashes inbetween but not at the start/end.
    __valid_name = re.compile("^[a-z][a-z-]*[a-z]+$")

    """A connection between a server and client."""

    _handle_message: Callable[[Message], None]

    def __init__(self, server: "Server", ws: WebSocketServerProtocol) -> None:
        self._server = server
        self._ws = ws
        self._message_factory = MessageFactory()
        self._reply_factory = ReplyFactory()
        self._name = ""
        self._handle_message = self._identify_handler

    async def _send(self, raw: str):
        await self._ws.send(raw)

    def _reply(self, r: Reply) -> None:
        reply_json = json.dumps(self._reply_factory.serialize(r))
        asyncio.create_task(self._send(reply_json))

    def _error(self, e: Error) -> None:
        error_json = json.dumps(e, default=encode_error)
        asyncio.create_task(self._send(error_json))

    def _log_address(self, msg: str):
        print(f"{self._ws.remote_address}: {msg}")

    # Handle only identify packets and reject other messages.
    def _identify_handler(self, message: Message):
        match message:
            case IdentifyMessage(name):
                self._log_address(f"identify as {name}")
                if not self.__valid_name.match(name):
                    self._error(InvalidUsernameError())
                    return

                if self._server.get_user(name):
                    self._error(NameInUseError(name))
                else:
                    print(f"Registering connection as user {name}")
                    self._server.add_user(self, name)
                    self._name = name
                    self._handle_message = self._regular_handler
            case _:  # Ignore other messages.
                pass

    # After registration we start the regular command loop.
    def _regular_handler(self, message: Message):
        match message:
            case SendMessage(content, where):
                self._log_address(f"{self._name} want to send to {where}:\n{content}")
            case _:  # Ignore other messages.
                pass

    def handle_message(self, message: Message) -> None:
        self._handle_message(message)

    def consume_raw(self, kind: str, data: JSONObject):
        try:
            message = self._message_factory.deserialize(kind, data)
            self.handle_message(message)
        except ValueError:
            print("Bad JSON received. Ignoring.")

    @property
    def name(self) -> str:
        return self._name


class Server:
    _connections: dict[WebSocketServerProtocol, Client]
    _users: dict[str, Client]  # Clients that have identified.

    _message_factory: MessageFactory

    def __init__(self) -> None:
        self._connections = {}
        self._users = {}

        self._message_factory = MessageFactory()

    def get_user(self, name: str) -> Optional[Client]:
        return self._users.get(name)

    def add_user(self, client: Client, name: str):
        self._users[name] = client

    async def handle_messages(self, ws: WebSocketServerProtocol):
        client = Client(self, ws)
        self._connections[ws] = client

        print(f"Connection from {ws.remote_address}")

        try:
            async for message in ws:
                payload: JSONObject = json.loads(message)
                kind = payload["kind"]
                data = payload["data"]
                client.consume_raw(kind, data)
        except ConnectionClosedError:
            pass
        finally:
            del self._connections[ws]
            if (name := client.name) and name in self._users:
                del self._users[name]

        print(f"Disconnection from {ws.remote_address}")

    async def listen(self, port: int):
        async with serve(self.handle_messages, "", port):
            await asyncio.Future()


async def main():
    parser = argparse.ArgumentParser("server")
    parser.add_argument("-p", "--port", type=int, default=8008)

    args = parser.parse_args()
    port: int = args.port

    server = Server()

    print(f"Hosting on ws://localhost:{port}")
    await server.listen(port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Terminating server.")
