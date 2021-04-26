import aiohttp

'https://www.vmr.gov.ua/Docs/_layouts/15/inplview.aspx?List={ECE62AE9-8D43-42E8-9FF1-CC98B48523E0}&View={691AA8F1-67B6-47BF-A590-39AF85829901}&ViewCount=1759&IsXslView=TRUE&IsCSR=TRUE&RootFolder=%2fDocs%2fExecutiveCommitteeDecisions%2f2021'
'https://www.vmr.gov.ua/Docs/_layouts/15/inplview.aspx?List={ECE62AE9-8D43-42E8-9FF1-CC98B48523E0}&View={691AA8F1-67B6-47BF-A590-39AF85829901}&ViewCount=1759&IsXslView=TRUE&IsCSR=TRUE&Paged=TRUE&p_SortBehavior=0&p_Created=20210416%2006%3a28%3a12&p_ID=36603&RootFolder=%2fDocs%2fExecutiveCommitteeDecisions%2f2021&PageFirstRow=31'
BASE_URL = 'https://www.vmr.gov.ua'
DATA_URL = BASE_URL + '/Docs/_layouts/15/inplview.aspx'
INITIAL_PARAMS = {
    'List': '{ECE62AE9-8D43-42E8-9FF1-CC98B48523E0}',
    'View': '{691AA8F1-67B6-47BF-A590-39AF85829901}',
    'IsXslView': 'TRUE',
    'IsCSR': 'TRUE',
    'Paged': 'TRUE',
    'PagedPrev': 'TRUE',
    'p_SortBehavior': '0',
    'p_ID': '36552',
    # 'RootFolder': '%2fDocs%2fExecutiveCommitteeDecisions%2f2021',
    'RootFolder': '/Docs/ExecutiveCommitteeDecisions/2021',
    # 'PageFirstRow': '1',
}
TITLE_KEY = '_x041f__x043e__x0432__x043d__x0430__x0020__x043d__x0430__x0437_' \
            '_x0432__x0430_'


async def parse():
    async with aiohttp.ClientSession() as session:
        params = {**INITIAL_PARAMS, 'PageFirstRow': 2}
        async with session.post(
                DATA_URL,
                params=params,
                timeout=10,
        ) as response:
            data = await response.json()
            row = data['Row'][0]
            print(row[TITLE_KEY])
            print(BASE_URL + row['FileRef'])
