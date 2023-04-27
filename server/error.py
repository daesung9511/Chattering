import abc
import enum
from enum import auto


class ErrorCode(enum.IntEnum):
    NAME_IN_USE = auto()
    INVALID_NAME = auto()


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
