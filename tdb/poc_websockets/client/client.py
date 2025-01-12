import asyncio
import logging
from asyncio import Queue

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMessage
from fastapi import APIRouter
from starlette.status import HTTP_200_OK
from yarl import URL

from tdb.poc_websockets.client.config import settings
from tdb.poc_websockets.server.routes.auth import login_token
from tdb.poc_websockets.server.routes.auth import router as auth_router
from tdb.poc_websockets.server.routes.websocket import router as websocket_router
from tdb.poc_websockets.server.routes.websocket import ws_room

logger = logging.getLogger(__name__)


class Client:
    def __init__(self) -> None:
        logger.debug('Initializing Client')

        self.base_url = URL.build(host=settings.APP_HOST, port=settings.APP_PORT)
        self.app_url = self.base_url.with_scheme(settings.APP_SCHEMA)

        self.login_uri = self.build_uri(settings.APP_SCHEMA, auth_router, login_token.__name__)
        self.ws_uri = self.build_uri('ws', websocket_router, ws_room.__name__, room='testRoom')

        self.consumer_queue: Queue[str | None] = Queue(-1)
        self.producer_queue: Queue[str | None] = Queue(-1)

    def build_uri(self, schema: str, router: APIRouter, function_name: str, **path_params: str) -> str:
        with_scheme = self.base_url.with_scheme(schema)
        uri_path = router.url_path_for(function_name, **path_params)
        return str(with_scheme.joinpath(uri_path[1:]))

    async def consumer(self, websocket: ClientWebSocketResponse) -> None:
        logger.debug('Starting consumer')

        message: WSMessage
        while True:
            async for message in websocket:
                if message.type == aiohttp.WSMsgType.TEXT:
                    data = message.data
                    logger.debug('consumer message: %s', data)
                    await self.consumer_queue.put(data)
                elif message.type == aiohttp.WSMsgType.ERROR:
                    logger.error('Websocket Error')
                    if not websocket.closed:
                        await websocket.close()
                        break

                else:
                    logger.error('Unexpected message type')
                    if not websocket.closed:
                        await websocket.close()
                        break

            if websocket.closed:
                break

        logger.debug('Exited consumer')

    async def producer(self, websocket: ClientWebSocketResponse) -> None:
        logger.debug('Starting producer')

        while True:
            message = await self.producer_queue.get()

            if message is None:
                logger.debug('Message queue is empty, closing loop')
                break

            logger.debug('Sending message: %s', message)
            await websocket.send_str(message)

        logger.debug('Exited producer')

    async def generate_message(self) -> None:
        logger.debug('Starting generator')

        import secrets

        random = secrets.SystemRandom()

        for r in range(10):
            random_number = random.randrange(5, 10 + 1)

            logger.debug('Sleeping for %d seconds [%d]', random_number, r)
            await self.producer_queue.put(f'Rand: {random_number}')
            await asyncio.sleep(random_number)

        await self.producer_queue.put(None)

        logger.debug('Exited generator')

    async def run(self) -> None:
        logger.debug('Login to Client: %s', self.login_uri)

        async with aiohttp.ClientSession() as session:
            login_data = {'grant_type': 'password', 'username': settings.USER, 'password': settings.PASS}

            async with session.post(self.login_uri, data=login_data) as response:
                if response.status == HTTP_200_OK:
                    logger.debug('Connecting to websocket')

                    async with session.ws_connect(self.ws_uri) as websocket:
                        logger.debug('Starting consumer / producer tasks')

                        async with asyncio.TaskGroup() as task_group:
                            task_group.create_task(self.consumer(websocket))
                            task_group.create_task(self.producer(websocket))
                            task_group.create_task(self.generate_message())

                        logger.debug('Exited consumer / producer tasks')

                    logger.debug('Exited websocket')

            logger.debug('Exited session')

        logger.debug('Exited client')
