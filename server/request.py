import abc
from dataclasses import dataclass
from typing import Any


class Request(abc.ABC):
    """Base class for all requests."""


@dataclass
class LoginRequest(Request):
    username: str


@dataclass
class MessageRequest(Request):
    author: str
    message: str


class RequestFactory:
    def deserialize_request(self, payload: dict[str, Any]) -> Request:
        ty = payload["type"]
        data = payload["data"]

        match ty:
            case "login":
                return LoginRequest(data["username"])
            case "message":
                return MessageRequest(
                    data["author"],
                    data["content"]
                )
            case _:
                raise ValueError()
