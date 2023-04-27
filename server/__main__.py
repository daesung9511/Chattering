import argparse
import asyncio
import json

from websockets.exceptions import ConnectionClosedError
from websockets.server import WebSocketServerProtocol, serve

from .message import MessageFactory, Message
from .types import JSONObject


class Client:
    def __init__(self, server: "Server", ws: WebSocketServerProtocol) -> None:
        self._server = server
        self._ws = ws
        self._message_factory = MessageFactory()

    def handle_message(self, message: Message) -> None:
        raise NotImplementedError(message)

    def consume_raw(self, kind: str, data: JSONObject):
        try:
            message = self._message_factory.deserialize(kind, data)
            self.handle_message(message)
        except ValueError:
            pass


class Server:
    _connections: dict[WebSocketServerProtocol, Client]

    def __init__(self) -> None:
        self._connections = {}

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
