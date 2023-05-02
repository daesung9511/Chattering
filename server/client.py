from __future__ import annotations

import asyncio
import json
import re
from typing import TYPE_CHECKING, Callable

from websockets.server import WebSocketServerProtocol

from .error import Error, InvalidUsernameError, NameInUseError, encode_error
from .message import IdentifyMessage, JoinMessage, Message, MessageFactory, SendMessage
from .reply import MessageReply, Reply, ReplyFactory, IdentifiedReply
from .types import JSONObject

if TYPE_CHECKING:
    from .channel import Channel
    from .server import Server


class Client:
    # lowercase names that can have dashes inbetween but not at the start/end.
    __valid_name = re.compile("^[a-z][a-z-]*[a-z]+$")

    """A connection between a server and client."""

    _handle_message: Callable[[Message], None]

    _channels: dict[str, Channel]

    def __init__(self, server: Server, ws: WebSocketServerProtocol) -> None:
        self._server = server
        self._ws = ws
        self._message_factory = MessageFactory()
        self._reply_factory = ReplyFactory()
        self._name = ""
        self._handle_message = self._identify_handler
        self._channels = {}

    def send_message(self, author: Client, message: str):
        self.reply(MessageReply(author.name, self.name, message))

    async def _send(self, raw: str):
        await self._ws.send(raw)

    def reply(self, message: Reply):
        raw = json.dumps(self._reply_factory.serialize(message))
        asyncio.create_task(self._send(raw))

    def _reply(self, r: Reply) -> None:
        reply_json = json.dumps(self._reply_factory.serialize(r))
        asyncio.create_task(self._send(reply_json))

    def error(self, e: Error) -> None:
        error_json = json.dumps(e, default=encode_error)
        asyncio.create_task(self._send(error_json))

    def _log_address(self, msg: str):
        if self._name:
            print(f"{self._ws.remote_address}, {self._name}: {msg}")
        else:
            print(f"{self._ws.remote_address}: {msg}")

    # Handle only identify packets and reject other messages.
    def _identify_handler(self, message: Message):
        match message:
            case IdentifyMessage(name):
                self._log_address(f"identify as {name}")
                if not self.__valid_name.match(name):
                    self.error(InvalidUsernameError())
                    return

                if self._server.get_user(name):
                    self.error(NameInUseError(name))
                else:
                    print(f"Registering connection as user {name}")
                    self._server.add_user(self, name)
                    self._name = name
                    self._handle_message = self._regular_handler
                    self.reply(IdentifiedReply()    )
            case _:  # Ignore other messages.
                pass

    # After registration we start the regular command loop.
    def _regular_handler(self, message: Message):
        match message:
            case SendMessage(content, where):
                self._log_address(f"sending to {where}:\n{content}")
                if user := self._server.get_user(where):
                    user.send_message(self, content)
                if channel := self._server.get_channel(where):
                    channel.send_message(self, content)
            case JoinMessage(where):
                self._log_address(f"joining channel {where}")
                if channel := self._server.get_channel(where):
                    self._channels[where] = channel
                    channel.add_user(self)
            case _:  # Ignore other messages.
                pass

    def handle_message(self, message: Message) -> None:
        self._handle_message(message)

    def consume_raw(self, kind: str, data: JSONObject):
        try:
            message = self._message_factory.deserialize(kind, data)
            self.handle_message(message)
        except ValueError:
            pass

    @property
    def name(self) -> str:
        return self._name
