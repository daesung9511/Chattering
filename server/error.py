import abc
import enum
from enum import auto

from .types import JSONObject


class ErrorCode(enum.IntEnum):
    NAME_IN_USE = auto()
    INVALID_NAME = auto()
    NOT_IN_CHANNEL = auto()


class Error(abc.ABC):
    @abc.abstractmethod
    def code(self) -> int:
        pass

    @abc.abstractmethod
    def message(self) -> str:
        pass


class NameInUseError(Error):
    def __init__(self, name: str) -> None:
        self.name = name

    def message(self) -> str:
        return f"Name {self.name} is in use."

    def code(self) -> int:
        return ErrorCode.NAME_IN_USE


class InvalidUsernameError(Error):
    def message(self) -> str:
        return "Invalid username."

    def code(self) -> int:
        return ErrorCode.NAME_IN_USE


class NotInChannelError(Error):
    def __init__(self, channel: str) -> None:
        self.channel = channel

    def message(self) -> str:
        return f"Not in channel {self.channel}."

    def code(self) -> int:
        return ErrorCode.NOT_IN_CHANNEL


# Error objects are simple so a regular decoder will do.
def encode_error(error: Error) -> JSONObject:
    return {"error": error.message(), "code": error.code()}
