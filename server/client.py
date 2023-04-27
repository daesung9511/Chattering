import asyncio
import json
import re
from typing import Callable

from websockets.server import WebSocketServerProtocol

from .error import Error, InvalidUsernameError, NameInUseError, encode_error
from .message import IdentifyMessage, Message, MessageFactory, SendMessage
from .reply import Reply, ReplyFactory
from .server import Server
from .types import JSONObject


class Client:
    # lowercase names that can have dashes inbetween but not at the start/end.
    __valid_name = re.compile("^[a-z][a-z-]*[a-z]+$")

    """A connection between a server and client."""

    _handle_message: Callable[[Message], None]

    def __init__(self, server: Server, ws: WebSocketServerProtocol) -> None:
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
