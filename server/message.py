"""
Requests from the client.

Things like identifying, sending text messages, and joining/leaving channels.
"""

import abc
from typing import Callable
import enum
import inspect


from .types import JSONObject


class MessageKind(enum.Enum):
    IDENTIFY = "identify"
    SEND = "send"
    JOIN = "join"
    PART = "part"


class Message(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def kind() -> MessageKind:
        pass


class IdentifyMessage(Message):
    __match_args__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def kind() -> MessageKind:
        return MessageKind.IDENTIFY


class SendMessage(Message):
    __match_args__ = ("content", "where")

    def __init__(self, content: str, where: str) -> None:
        self.content = content
        self.where = where

    @staticmethod
    def kind() -> MessageKind:
        return MessageKind.SEND


class JoinMessage(Message):
    __match_args__ = ("where",)

    def __init__(self, where: str) -> None:
        self.where = where

    @staticmethod
    def kind() -> MessageKind:
        return MessageKind.JOIN


class LeaveMessage(Message):
    __match_args__ = ("where",)

    def __init__(self, where: str) -> None:
        self.where = where

    @staticmethod
    def kind() -> MessageKind:
        return MessageKind.PART


class MessageFactory:
    __handlers: dict[str, Callable[[JSONObject], Message]]

    def __init__(self) -> None:
        self.__handlers = {}

        for name, value in inspect.getmembers(self):
            if name.startswith("deserialize_"):
                self.__handlers[name[len("deserialize_") :]] = value

    def deserialize(self, kind: str, data: JSONObject):
        if handler := self.__handlers.get(kind):
            return handler(data)

        raise ValueError(f"Message kind {kind} is not valid!")

    def deserialize_identify(self, data: JSONObject) -> Message:
        return IdentifyMessage(data["name"])

    def deserialize_send(self, data: JSONObject) -> Message:
        return SendMessage(data["content"], data["where"])

    def deserialize_join(self, data: JSONObject) -> Message:
        return JoinMessage(data["where"])

    def deserialize_leave(self, data: JSONObject) -> Message:
        return LeaveMessage(data["where"])
