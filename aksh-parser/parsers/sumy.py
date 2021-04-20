import json
import logging
from asyncio import sleep
from base64 import b64encode
from io import StringIO

import aiohttp
from aiofile import async_open
from lxml import etree

logger = logging.getLogger(__name__)


BASE_URL = 'https://smr.gov.ua'
PAGE_URI = '/uk/dokumenti/rishennya-miskoji-radi/2021.html'
XPATH = '/html/body/div[3]/div/div[2]/div[1]/div/div[2]/div/div/div/div[4]' \
        '/div[2]/div/table/tbody/tr[position()>=2]/td[2]/a'


async def parse():
    # Get the page with all acts
    logger.info('Reading from %s', BASE_URL)
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + PAGE_URI, timeout=10) as response:
            page = await response.text()
    logger.info('Reading from %s finished', BASE_URL)

    # Get the <a> tags with the acts data
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(page), htmlparser)
    links = tree.xpath(XPATH)

    results = [{
        'link': BASE_URL + link.get('href'),  # act's link
        'title': link.text,  # act's title
    } for link in links]
    n_results = len(results)

    logger.info('Writing results:')
    async with async_open("data/sumy.json", 'w') as af:
        # Writing a JSON manually because the json library does not support
        # writing with chunks.
        await af.write('[\n')
        for i, result in enumerate(results):
            # Get binary of the act's file and convert to base64
            async with aiohttp.ClientSession() as session:
                async with session.get(result['link'], timeout=10) as response:
                    file_content = await response.read()
            base_64 = b64encode(file_content).decode()

            # Write a row into the file
            await af.write('  ')
            row = json.dumps({**result, 'file': base_64}, ensure_ascii=False)
            await af.write(row)
            if not i == n_results - 1:
                await af.write(',')
            await af.write('\n')

            await sleep(2)  # don't overload the server
            logger.info('  %d out of %d ready', i + 1, n_results)
        await af.write(']\n')

    logger.info('Writing results finished')
