#!/usr/bin/env python

# TODO: make it a FastAPI application

import logging
import asyncio

from parsers import (
    sumy,
    # vinnytsia,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


cities = [
    sumy,
    # vinnytsia,
]


if __name__ == '__main__':
    logger.info('Running %s parsers', len(cities))

    futures = [city.parse() for city in cities]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))
