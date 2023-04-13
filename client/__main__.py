from websockets.sync.client import ClientConnection, connect

if __name__ == "__main__":
    port = 42069
    url = f"ws://localhost:{port}/connect"
    print(f"connecting to {url}!")
    with connect(url) as ws:
        ws: ClientConnection
        ws.send("Hello, world!")
        print("Sent hello world!")
