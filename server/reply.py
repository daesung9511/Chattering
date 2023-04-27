"""
Responses from the server.

Includes things such as receiving messages from channels or messages.
As well as errors.
"""

import abc
import enum
from enum import auto


class ErrorCode(enum.IntEnum):
    NAME_IN_USE = auto()


class Reply(abc.ABC):
    pass


# TODO(Antonio): Implement User type
class MessageReply(Reply):
    def __init__(self, author: ...) -> None:
        pass


# ERRORS


class ErrorReply(Reply):
    @abc.abstractmethod
    def code(self) -> int:
        pass

    @abc.abstractmethod
    def message(self) -> str:
        pass


class PleaseIdentifyReply(ErrorReply):
    pass


class NameInUseReply(ErrorReply):
    def __init__(self, name: str) -> None:
        self.name = name

    def message(self) -> str:
        return f"Name {self.name} is in use."

    def code(self) -> int:
        return ErrorCode.NAME_IN_USE
