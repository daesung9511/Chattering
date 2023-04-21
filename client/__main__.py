import argparse
import json

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Label, TextLog
from websockets import InvalidURI
from websockets.sync.client import ClientConnection, connect


def old_main():
    parser = argparse.ArgumentParser("client", "client <host> <port> <channel>")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("channel")
    parser.add_argument("-u", "--user", help="Specify user name.", default="test-user")

    args = parser.parse_args()

    host: str = args.host
    port: int = args.port
    username: str = args.user
    url = f"ws://{host}:{port}/connect"
    print(f"Connecting to '{url}'...")
    try:
        with connect(url) as ws:
            ws: ClientConnection

            # Login into server.
            login = {"type": "login", "data": {"username": username}}
            ws.send(json.dumps(login))

            message_string: str = input("Input a message: ")
            message = {
                "type": "message",
                "data": {"author": "test-user", "content": message_string},
            }
            ws.send(json.dumps(message))
    except InvalidURI:
        print(f"URL {url} isn't a valid URI.")
    except OSError:
        print("Could not connect via TCP.")


class ChatteringClient(App):
    CSS_PATH = "chattering.css"

    info_label: Label
    text_input: Input
    text_log: TextLog
    messages_sent: int

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()

        self.messages_sent = 0
        with Vertical():
            self.text_input = Input(placeholder="Send a message!")
            self.text_log = TextLog(classes="box")
            self.info_label = Label("No messages sent...", classes="label")

            yield self.text_log
            yield self.info_label
            yield self.text_input

        yield Footer()

    def on_input_submitted(self):
        if not self.text_input.value:
            return

        self.text_log.write(self.text_input.value)
        with self.text_input.prevent(Input.Changed):
            self.text_input.value = ""
        self.messages_sent += 1
        self.info_label.update(f"Messages sent: {self.messages_sent}")


if __name__ == "__main__":
    app = ChatteringClient()
    app.run()
