from __future__ import annotations

from typing import TYPE_CHECKING

from .reply import MessageReply
from .error import NotInChannelError

if TYPE_CHECKING:
    from .client import Client
    from .server import Server


class Channel:
    users: set[Client]

    def __init__(self, server: Server, name: str) -> None:
        self.server = server
        self.name = name
        self.users = set()

    def add_user(self, user: Client):
        self.users.add(user)

    def remove_user(self, user: Client):
        self.users.remove(user)

    def send_message(self, author: Client, message: str):
        print(f"User {author.name} sent to channel {self.name}:\n{message}")
        if author not in self.users:
            author.error(NotInChannelError(self.name))
            return

        for user in self.users:
            if user == author:
                continue  # Don't resend to self.
            user.reply(MessageReply(author.name, self.name, message))
