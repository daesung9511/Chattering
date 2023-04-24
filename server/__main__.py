import argparse
import asyncio
import json
import re
from dataclasses import asdict
from typing import Callable, Optional, Union

import error
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from .request import LoginRequest, Request, RequestFactory

VALID_NICKNAME = re.compile("^[a-zA-Z]+$")

RequestHandler = Callable[[Request], None]


class Client:
    __handle_request: RequestHandler

    def __init__(
        self, server: "ChatteringApplication", connection: "ConnectHandler"
    ) -> None:
        self.name = ""
        self.server = server
        self.connection = connection

    def error(self, error: error.Error):
        self.connection.write(json.dumps(asdict(error)))

    def reply(self, message: str):
        self.connection.write(message)

    def __handle_regular(self, message: Request):
        raise NotImplementedError()

    def __handle_login(self, message: Request):
        match message:
            case LoginRequest(username):
                if not VALID_NICKNAME.match(username):
                    self.error(error.bad_username())

                if self.server.get_client_by_username(username):
                    self.error(error.username_taken(username))
                else:
                    # Set message handler to 
                    self.name = username
                    self.__handle_request = self.__handle_regular
            case _:
                self.error(error.unknown_request())

    def handle_request(self, message: Request):
        print(f"handle_request: {message}")
        self.__handle_request(message)


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
        try:
            json_message = json.loads(raw_message)
            request = self.request_factory.deserialize_request(json_message)
            try:
                self.client.handle_request(request)
            except ValueError:
                print(f"Unknown request type '{json_message['type']}'")
        except json.JSONDecodeError:
            print(f"Bad json request:\n\t{raw_message}")


class ChatteringApplication(Application):
    __connections: dict[ConnectHandler, Client]
    __conn_by_username: dict[str, Client]

    def __init__(self) -> None:
        handlers = [
            (r"/connect", ConnectHandler, dict(server=self)),
        ]
        super().__init__(handlers)

        self.__connections = {}
        self.__conn_by_username = {}

    def get_client_by_username(self, username: str) -> Optional[Client]:
        return self.__conn_by_username.get(username)

    def add_client(self, connection: ConnectHandler):
        self.__connections[connection] = Client(self, connection)

    def remove_client(self, connection: ConnectHandler):
        del self.__connections[connection]


async def main():
    parser = argparse.ArgumentParser("server", "server <port>")
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    port: int = args.port
    app = ChatteringApplication()
    server = HTTPServer(app)  # TODO(Antonio): Pass SSL context here with custom cert.
    server.listen(port)
    print(f"Listening on port {port}.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Catch to prevent showing stack trace to user.
        print("Server stopped.")
