"""
Requests from the client.

Things like identifying, sending text messages, and joining/leaving channels.
"""

import abc
from typing import Callable

from .types import JSONObject


# TODO(Antonio): Include source?
# Maybe not... the server knows who sent the message so we can attach it later.
# Probably in the reply like
class Message(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def kind() -> str:
        pass


class IdentifyMessage(Message):
    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def kind() -> str:
        return "identify"


class SendMessage(Message):
    def __init__(self, source: str, target: str, text: str) -> None:
        self.source = source
        self.target = target
        self.text = text

    @staticmethod
    def kind() -> str:
        return "send"


class JoinMessage(Message):
    @staticmethod
    def kind() -> str:
        return "join"


class PartMessage(Message):
    @staticmethod
    def kind() -> str:
        return "part"


class MessageFactory:
    __handlers: dict[str, Callable[[JSONObject], Message]]

    def __init__(self) -> None:
        self.__handlers = {
            IdentifyMessage.kind(): self.deserialize_identify_message,
            SendMessage.kind(): self.deserialize_send_message,
        }

    def test(self) -> Message:
        return IdentifyMessage("foo")

    def deserialize(self, kind: str, data: JSONObject):
        if handler := self.__handlers.get(kind):
            return handler(data)

        raise ValueError(f"Message kind {kind} is not valid!")

    def deserialize_identify_message(self, data: JSONObject) -> Message:
        return IdentifyMessage(data["name"])

    def deserialize_send_message(self, data: JSONObject) -> Message:
        return SendMessage(data["source"], data["target"], data["text"])
