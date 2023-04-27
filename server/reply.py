"""
Responses from the server.

Includes things such as receiving messages from channels or messages.
As well as errors.
"""

import abc


class Reply(abc.ABC):
    pass


# TODO(Antonio): Implement User type
class MessageReply(Reply):
    def __init__(self, author: ...) -> None:
        pass
