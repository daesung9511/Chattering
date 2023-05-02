import argparse
import asyncio
import ssl
import pathlib

from .server import Server


async def main():
    parser = argparse.ArgumentParser("server")
    parser.add_argument("-p", "--port", type=int, default=8008)
    parser.add_argument("-c", "--cert")
    parser.add_argument("-k", "--key")

    args = parser.parse_args()
    port: int = args.port

    server = None
    if args.cert and args.key:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cert = pathlib.Path(args.cert)
        key = pathlib.Path(args.key)
        ssl_context.load_cert_chain(cert, keyfile=key)
        server = Server(ssl_context)
    else:
        server = Server()

    print(f"Hosting on {'wss' if args.cert else 'ws'}://localhost:{port}")
    await server.listen(port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Terminating server.")
