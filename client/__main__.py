import argparse
import json

from websockets import InvalidURI
from websockets.sync.client import ClientConnection, connect

if __name__ == "__main__":
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
            login = {
                "type": "login",
                "data": {
                    "username": username
                }
            }
            ws.send(json.dumps(login))

            message_string: str = input("Input a message: ")
            message = {
                "type": "message",
                "data": {
                    "author": "test-user",
                    "content": message_string
                }
            }
            ws.send(json.dumps(message))
    except InvalidURI:
        print(f"URL {url} isn't a valid URI.")
    except OSError:
        print("Could not connect via TCP.")
