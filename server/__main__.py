import argparse
import asyncio
import json
from typing import Union

from tornado.web import Application
from tornado.websocket import WebSocketHandler

from .request import Request, RequestFactory


class Client:
    def __init__(
            self, server: "ChatteringApplication", connection: "ConnectHandler"
    ) -> None:
        self.name = ""
        self.server = server
        self.connection = connection

    def handle_request(self, message: Request):
        print(f"handle_request: {message}")


class ConnectHandler(WebSocketHandler):
    server: "ChatteringApplication"
    client: Client
    request_factory: RequestFactory

    def initialize(self, server: "ChatteringApplication"):
        self.server = server
        self.client = Client(server, self)
        self.request_factory = RequestFactory()

    def open(self):
        print(f"Connection from {self.request.remote_ip} opened.")
        self.server.add_client(self)

    def on_close(self):
        print(f"Connection from {self.request.remote_ip} closed.")
        self.server.remove_client(self)

    def on_message(self, raw_message: Union[str, bytes]):
        print(f"{self.request.remote_ip} sent {raw_message}")
        try:
            json_message = json.loads(raw_message)
            request = self.request_factory.deserialize_request(json_message)
            try:
                self.client.handle_request(request)
            except ValueError:
                print(f"Unknown request type '{json_message['ty']}'")
        except json.JSONDecodeError:
            print("Bad json request. Ignoring.")


class ChatteringApplication(Application):
    connections: dict[ConnectHandler, Client]

    def __init__(self) -> None:
        handlers = [
            (r"/connect", ConnectHandler, dict(server=self)),
        ]
        super().__init__(handlers)

        self.connections = {}

    def add_client(self, connection: ConnectHandler):
        self.connections[connection] = Client(self, connection)

    def remove_client(self, connection: ConnectHandler):
        del self.connections[connection]


async def main():
    parser = argparse.ArgumentParser("server", "server <port>")
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    port: int = args.port
    app = ChatteringApplication()
    print(f"Listening on port {port}.")
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Catch to prevent showing stack trace to user.
        print("Server stopped.")
