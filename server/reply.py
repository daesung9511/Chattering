"""
Responses from the server.

Includes things such as receiving messages from channels or messages.
As well as errors.
"""

import abc

from .types import JSONObject


class Reply(abc.ABC):
    pass


class IdentifiedReply(Reply):
    __match_args__ = ()


class MessageReply(Reply):
    __match_args__ = ("author", "where", "content")

    def __init__(self, author: str, where: str, content: str) -> None:
        self.author = author
        self.where = where
        self.content = content


class JoinedReply(Reply):
    __match_args__ = ("where",)

    def __init__(self, where: str) -> None:
        self.where = where


class ListChannelsReply(Reply):
    __match_args__ = ("channels",)

    def __init__(self, channels: list[str]) -> None:
        self.channels = channels


class ReplyFactory:
    def serialize(self, reply: Reply) -> JSONObject:
        match reply:
            case MessageReply(author, where, content):
                return {
                    "kind": "message",
                    "data": {"author": author, "where": where, "content": content},
                }

            case JoinedReply(where):
                return {"kind": "join", "data": {"where": where}}
            case IdentifiedReply():
                return {"kind": "identified", "data": {}}
            case ListChannelsReply(channels):
                return {"kind": "list_channels", "data": {"channels": channels}}
            case _:
                raise ValueError(f"Invalid reply object: {reply}")
