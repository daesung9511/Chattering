from dataclasses import dataclass
from enum import IntEnum, auto, unique


@unique 
class ErrorCode(IntEnum):
    USERNAME_TAKEN = auto()
    UNKNOWN_REQUEST = auto()
    BAD_USERNAME = auto()


@dataclass
class Error:
    code: ErrorCode
    message: str


def username_taken(name: str) -> Error:
    return Error(ErrorCode.USERNAME_TAKEN, f"Username {name} is taken.")


def unknown_request(message: str = "Unknown request.") -> Error:
    return Error(ErrorCode.UNKNOWN_REQUEST, message)


def bad_username() -> Error:
    return Error(ErrorCode.BAD_USERNAME, "Username contains invalid characters.")
