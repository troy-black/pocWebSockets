from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # WebSockets by room and user
        self.active_connections: dict[str, dict[str, WebSocket]] = defaultdict(lambda: defaultdict())

    # make connection
    async def connect(self, websocket: WebSocket, /, *, room: str, user: str) -> None:
        await websocket.accept()

        self.active_connections[room][user] = websocket

    def disconnect(self, /, *, room: str, user: str) -> None:
        self.active_connections[room].pop(user)

    async def send_message(self, message: str, /, *, room: str, user: str) -> None:
        websocket = self.active_connections[room][user]

        await websocket.send_text(message)

    async def broadcast(self, message: str, /, *, room: str, sending_user: str) -> None:
        for user, websocket in self.active_connections[room].items():
            if user != sending_user:
                await websocket.send_text(message)


manager = ConnectionManager()
