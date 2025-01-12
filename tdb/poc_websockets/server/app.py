import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import fastapi
from starlette import staticfiles
from starlette.middleware.cors import CORSMiddleware

from tdb.poc_websockets.server import config
from tdb.poc_websockets.server.logger import force_logging
from tdb.poc_websockets.server.routes import auth, room, status, websocket
from tdb.poc_websockets.server.routes.v1 import user


@asynccontextmanager
async def lifespan(_fast_api: fastapi.FastAPI) -> AsyncGenerator[None, None]:
    force_logging()

    logger = logging.getLogger(__name__)
    # on_startup
    logger.debug('Application Startup')
    yield None
    # on_shutdown
    logger.debug('Application Shutdown')


settings = config.settings
origins = [f'{settings.APP_SCHEMA}://{settings.APP_HOST}:{settings.APP_PORT}']


app = fastapi.FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url='/docs',
    lifespan=lifespan,
)

# Set up CORS middleware
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(status.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(websocket.router)
app.include_router(room.router)

app.mount(
    '/static',
    staticfiles.StaticFiles(directory=settings.STATIC),
    name='static',
)
