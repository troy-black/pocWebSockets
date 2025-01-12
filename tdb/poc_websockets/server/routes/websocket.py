from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from tdb.poc_websockets.server import auth, database
from tdb.poc_websockets.server.websocket import manager

router = APIRouter(
    prefix='/websocket',
    tags=['websocket'],
)


@router.websocket('/{room}')
async def ws_room(
    socket: WebSocket,
    room: str,
    access_token: Annotated[str, Cookie()],
    db: Annotated[AsyncSession, Depends(database.get_session)],
) -> None:
    token = access_token.split('Bearer')[1].strip()
    current_user = await auth.get_current_user(token, db)
    email = current_user.email

    await manager.connect(socket, room=room, user=email)

    await manager.send_message(f'You ({email}) joined room: {room}', room=room, user=email)
    await manager.broadcast(f'User {email} joined room: {room}', room=room, sending_user=email)

    try:
        while True:
            data = await socket.receive_text()
            msg = f'{email}: {data}'
            await manager.broadcast(msg, room=room, sending_user=email)

    except WebSocketDisconnect:
        manager.disconnect(room=room, user=email)
        await manager.broadcast(f'User {email} left room: {room}', room=room, sending_user=email)
