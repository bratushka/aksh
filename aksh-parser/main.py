import logging
import asyncio
from pathlib import Path

from parsers import sumy


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


cities = [
    sumy,
]


if __name__ == '__main__':
    logger.info('Running parsers, %s to go', len(cities))
    Path('data').mkdir(exist_ok=True)

    futures = [city.parse() for city in cities]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))
