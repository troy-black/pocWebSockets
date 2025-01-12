from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from tdb.poc_websockets.server.routes import templates

router = APIRouter(
    prefix='/example/room',
    tags=['room'],
)


@router.get('/{room}')
async def html_room(request: Request, room: str) -> HTMLResponse:
    return templates.TemplateResponse('room.html.jinja', {'request': request, 'room': room})
