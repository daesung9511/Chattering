"""
Responses from the server.

Includes things such as receiving messages from channels or messages.
As well as errors.
"""

import abc
from .types import JSONObject


class Reply(abc.ABC):
    pass


class MessageReply(Reply):
    __match_args__ = ("author", "where", "content")

    def __init__(self, author: str, where: str, content: str) -> None:
        self.author = author
        self.where = where
        self.content = content


# TODO(Antonio): Rework to use inspect over manually matching.
class ReplyFactory:
    def serialize(self, reply: Reply) -> JSONObject:
        match reply:
            case MessageReply(author, where, content):
                return {
                    "kind": "message",
                    "data": {"author": author, "where": where, "content": content},
                }
            case _:
                raise ValueError(f"Invalid reply object: {reply}")
