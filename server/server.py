import asyncio
import json
from json import JSONDecodeError
from typing import Optional
from ssl import SSLContext

from websockets.exceptions import ConnectionClosedError
from websockets.server import WebSocketServerProtocol, serve

from .channel import Channel
from .client import Client
from .message import MessageFactory
from .types import JSONObject
from ratelimit import limits, RateLimitException


class Server:
    _connections: dict[WebSocketServerProtocol, Client]
    _users: dict[str, Client]  # Clients that have identified.
    _channels: dict[str, Channel]
    _passwds: dict[str, str]  # name to password

    _message_factory: MessageFactory

    def __init__(self, ssl: Optional[SSLContext] = None) -> None:
        self._connections = {}
        self._users = {}
        self._channels = {}
        self._passwds = {}

        self._ssl = ssl

        self._message_factory = MessageFactory()

    def get_channel_names(self) -> list[str]:
        return list(self._channels.keys())

    def get_user(self, name: str) -> Optional[Client]:
        return self._users.get(name)

    def get_channel(self, name: str) -> Optional[Channel]:
        # TODO(Antonio): Lowercase name
        if name in self._channels:
            return self._channels[name]
        else:  # Create channel if it doesn't exist.
            print(f"Creating channel called {name}")
            channel = Channel(self, name)
            self._channels[name] = channel
            return channel

    def add_passwd(self, name: str, passwd: str):
        self._passwds[name] = passwd

    def has_passwd(self, name: str) -> bool:
        return name in self._passwds

    def check_passwd(self, name: str, passwd: Optional[str]) -> bool:
        if right_passwd := self._passwds.get(name):  # Check if name has passwd.
            return passwd == right_passwd  # Validate passwd.

        return True  # Otherwise the name has no passwd.

    def add_user(self, client: Client, name: str):
        self._users[name] = client

    async def handle_messages(self, ws: WebSocketServerProtocol):
        client = Client(self, ws)
        self._connections[ws] = client

        print(f"Connection from {ws.remote_address}")
        limit_for_each_connection = limits(calls=15, period=900, raise_on_limit=True)
        try:
            async for message in ws:
                try:
                    payload: JSONObject = json.loads(message)
                    kind = payload["kind"]
                    data = payload["data"]
                    limit_for_each_connection.__call__(client.consume_raw)(kind, data)
                except JSONDecodeError as ex:
                    print(f"Bad JSON, error at {ex.lineno}:{ex.pos}. Ignoring:")
                    print(ex.doc)

        except ConnectionClosedError:
            pass
        except RateLimitException:
            pass
        finally:
            del self._connections[ws]
            if (name := client.name) and name in self._users:
                # Remove user from each channel they're in.
                user = self._users[name]
                for channel in user.channels:
                    channel.remove_user(user)

                # And finally remove them from the users.
                del self._users[name]
        print(f"Disconnection from {ws.remote_address}")

    async def listen(self, port: int):
        async with serve(self.handle_messages, "", port, ssl=self._ssl):
            await asyncio.Future()
