import asyncio
import json
from typing import Optional

from websockets.exceptions import ConnectionClosedError
from websockets.server import WebSocketServerProtocol, serve

from .client import Client
from .message import MessageFactory
from .types import JSONObject


class Server:
    _connections: dict[WebSocketServerProtocol, Client]
    _users: dict[str, Client]  # Clients that have identified.

    _message_factory: MessageFactory

    def __init__(self) -> None:
        self._connections = {}
        self._users = {}

        self._message_factory = MessageFactory()

    def get_user(self, name: str) -> Optional[Client]:
        return self._users.get(name)

    def add_user(self, client: Client, name: str):
        self._users[name] = client

    async def handle_messages(self, ws: WebSocketServerProtocol):
        client = Client(self, ws)
        self._connections[ws] = client

        print(f"Connection from {ws.remote_address}")

        try:
            async for message in ws:
                payload: JSONObject = json.loads(message)
                kind = payload["kind"]
                data = payload["data"]
                client.consume_raw(kind, data)
        except ConnectionClosedError:
            pass
        finally:
            del self._connections[ws]
            if (name := client.name) and name in self._users:
                del self._users[name]

        print(f"Disconnection from {ws.remote_address}")

    async def listen(self, port: int):
        async with serve(self.handle_messages, "", port):
            await asyncio.Future()
