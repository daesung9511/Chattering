import asyncio
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from typing import Union, Optional, Awaitable

class ConnectHandler(WebSocketHandler):
    def open(self):
        print("Someone has connected!")
        pass

    def on_close(self):
        print("Someone has left.")
        pass

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        print(f"Someone sent a message of {message}")


class ChatteringApplication(Application):
    def __init__(self) -> None:
        handlers = [(r"/connect", ConnectHandler)]
        super().__init__(handlers)


async def main():
    port = 42069
    app = ChatteringApplication()
    print(f"Listening on port {port}")
    app.listen(port)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
