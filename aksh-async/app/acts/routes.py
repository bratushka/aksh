import asyncio

from fastapi import APIRouter, WebSocket

from . import parsers
from .acts_processors import ActsProcessor


router = APIRouter()


async def ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.receive_text()

    queue = asyncio.Queue()
    acts_processor = ActsProcessor(
        queue,
        # ('Sumy', parsers.sumy.parse),
        (parsers.dnipro.ISSUER, parsers.dnipro.parse),
    )
    asyncio.ensure_future(acts_processor.do_the_job())

    while True:
        message = await queue.get()
        if message == 'done':
            break
        await websocket.send_json(message)
