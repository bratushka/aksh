import asyncio
import datetime
import logging
from io import StringIO
# noinspection PyPep8Naming
import typing as T

import aiohttp
from lxml import etree

from app.acts.structures import Act, Document


logger = logging.getLogger(__name__)


ISSUER = 'Dnipro'
BASE_URL = 'https://dniprorada.gov.ua/'
PAGE_URI = 'uk/Widgets/GetAcceptCouncilDocuments'
MEDIA_URI = '/uk/Widgets/GetWidgetContent?url='
# xPath cheatsheet https://devhints.io/xpath
XPATH = '/html/body/div[2]/table/tbody/tr'


async def parse(inform: T.Callable[[str], T.Awaitable]) -> T.Mapping[str, Act]:
    await inform('Running `dnipro` parser')

    # Get the page with all acts
    await inform(f'Reading from {BASE_URL}')
    async with aiohttp.ClientSession() as session:
        async with session.post(
                BASE_URL + PAGE_URI,
                json={
                    "BegDocDate": "01.01.2021",
                    "EndDocDate": datetime.date.today().strftime('%d.%m.%Y'),
                },
                timeout=60,
        ) as response:
            html = await response.text()
    await inform(f'Reading from {BASE_URL} finished')

    # Get the <tr> tags with the acts data
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), htmlparser)
    rows = tree.xpath(XPATH)

    results = {}
    for row in rows:
        act_id = row.xpath('./td[2]/text()')[0].strip()
        title = row.xpath('./td[5]/text()')[0].strip()

        download_pdf = row.xpath('./td[6]/button/@onclick')
        download_doc = row.xpath('./td[7]/button/@onclick')
        if download_doc:
            url = BASE_URL + MEDIA_URI + download_doc[0].split('\'')[1]
        elif download_pdf:
            url = BASE_URL + MEDIA_URI + download_pdf[0].split('\'')[1]
        else:
            continue

        documents = [Document(order=0, url=url)]

        results[act_id] = Act(
            issuer=ISSUER,
            act_id=act_id,
            title=title,
            documents=documents,
        )
    await inform('Running `dnipro` parser finished')

    return results
