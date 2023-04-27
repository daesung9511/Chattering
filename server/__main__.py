import argparse
import asyncio

from .server import Server


async def main():
    parser = argparse.ArgumentParser("server")
    parser.add_argument("-p", "--port", type=int, default=8008)

    args = parser.parse_args()
    port: int = args.port

    server = Server()

    print(f"Hosting on ws://localhost:{port}")
    await server.listen(port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Terminating server.")
