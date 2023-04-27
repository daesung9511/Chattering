"""
Requests from the client.

Things like identifying, sending text messages, and joining/leaving channels.
"""

import abc
from typing import Callable

from .types import JSONObject


class Message(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def kind() -> str:
        pass


class IdentifyMessage(Message):
    __match_args__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def kind() -> str:
        return "identify"


class SendMessage(Message):
    __match_args__ = ("content", "text")

    def __init__(self, content: str, text: str) -> None:
        self.content = content
        self.text = text

    @staticmethod
    def kind() -> str:
        return "send"


class JoinMessage(Message):
    __match_args__ = ("join",)

    def __init__(self, where: str) -> None:
        self.where = where

    @staticmethod
    def kind() -> str:
        return "join"


class PartMessage(Message):
    __match_args__ = ("part",)

    def __init__(self, where: str) -> None:
        self.where = where

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

    def deserialize(self, kind: str, data: JSONObject):
        if handler := self.__handlers.get(kind):
            return handler(data)

        raise ValueError(f"Message kind {kind} is not valid!")

    def deserialize_identify_message(self, data: JSONObject) -> Message:
        return IdentifyMessage(data["name"])

    def deserialize_send_message(self, data: JSONObject) -> Message:
        return SendMessage(data["content"], data["text"])
