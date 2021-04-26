import asyncio
import logging
import pathlib
from datetime import datetime
from email.utils import parsedate_tz
from io import StringIO

import aiohttp
from lxml import etree

from services import API
from structures import Act, Document


logger = logging.getLogger(__name__)


ISSUER = 'Sumy'
MEDIA_DIR = pathlib.Path(f'/api-data/acts/{ISSUER}')
BASE_URL = 'https://smr.gov.ua'
# noinspection SpellCheckingInspection
PAGE_URI = '/uk/dokumenti/rishennya-miskoji-radi/2021.html'
# xPath cheatsheet https://devhints.io/xpath
XPATH = '/html/body/div[3]/div/div[2]/div[1]/div/div[2]/div/div/div/div[4]' \
        '/div[2]/div/table/tbody/tr[position()>=2]'

MEDIA_DIR.mkdir(exist_ok=True, parents=True)


async def parse():
    for line in '''
        Running `sumy` parser.
        Stages:
            1. Get acts' titles and links
            2. Store stage-1 data to the database and mark the removed ones
            3. Download every missing document
            4. Send data to the Shtab API
    '''.splitlines():
        logger.info(line[4:])

    # Get the page with all acts
    logger.info('    === Stage 1 ===')
    logger.info('    Get acts\' titles and links')
    logger.info('Reading from %s', BASE_URL)
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + PAGE_URI, timeout=10) as response:
            html = await response.text()
    logger.info('Reading from %s finished', BASE_URL)

    # Get the <a> tags with the acts data
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), htmlparser)
    rows = tree.xpath(XPATH)

    results = {}
    for row in rows:
        uris = row.xpath('./td[2]//@href')
        if not uris:
            continue

        act_id = row.xpath('./td[1]/text()')[0].strip()
        title = row.xpath('./td[2]//text()')[0].strip()
        documents = [
            Document(order=i, url=BASE_URL + uri.strip())
            for i, uri in enumerate(uris)
        ]

        results[act_id] = Act(
            issuer=ISSUER,
            act_id=act_id,
            title=title,
            documents=documents,
        )

    logger.info('Stage 1 complete, total of %d results found', len(results))

    logger.info('    === Stage 2 ===    ')
    logger.info('    Store stage-1 data to the database')

    acts = {
        act.act_id: act
        for act in await API.fetch_acts(issuer=ISSUER)
    }

    logger.info('Storing title/link pairs')

    for act_id, act in results.items():
        if act_id in acts:
            del acts[act_id]
        else:
            await API.create_act(act)

    logger.info('Marking the removed from source acts')
    for act in acts.values():
        await API.change_act(act.id, removed_from_source=True)

    logger.info('    === Stage 3 ===    ')
    logger.info('    Download every missing document')
    docs_without_files = await API.fetch_documents(needs_file=1)
    total = len(docs_without_files)
    logger.info('Missing documents: %d', total)

    for i, document in enumerate(docs_without_files, 1):
        logger.info('Downloading %d document out of %d', i, total)
        async with aiohttp.ClientSession() as session:
            async with session.get(document.url, timeout=60) as response:
                file_name = document.url.rsplit('/', 1)[1]
                last_modified = response.headers.get('Last-Modified')
                lm_datetime = datetime(*parsedate_tz(last_modified)[:6])
                files = [('file', file_name, await response.read())]
                await API.change_document(
                    document.id,
                    files=files,
                    last_modified=str(lm_datetime),
                )
                await asyncio.sleep(1)

    logger.info('%d documents downloaded', total)

    logger.info('Running `sumy` parser finished.')
