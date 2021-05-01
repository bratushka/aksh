import logging
import pathlib
from io import StringIO
# noinspection PyPep8Naming
import typing as T

import aiohttp
from lxml import etree

from app.acts.structures import Act, Document


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


async def parse(inform: T.Callable[[str], T.Awaitable]) -> T.Mapping[str, Act]:
    await inform('Running `sumy` parser')

    # Get the page with all acts
    await inform(f'Reading from {BASE_URL}')
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + PAGE_URI, timeout=10) as response:
            html = await response.text()
    await inform(f'Reading from {BASE_URL} finished')

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
    await inform('Running `sumy` parser finished')

    return results
