import asyncio
import logging
import pathlib
from datetime import datetime
from email.utils import parsedate_tz
# noinspection PyPep8Naming
import typing as T

import aiohttp
import filetype
import textract

from app.acts.structures import Act
from .services import API, Interest


logger = logging.getLogger(__name__)


class ActsProcessor:
    def __init__(
            self,
            message_queue: asyncio.Queue,
            *parsers: T.Tuple[
                str,
                T.Callable[[T.Callable], T.Awaitable[T.Mapping[str, Act]]],
            ],
    ):
        self.message_queue = message_queue
        self.parsers = parsers

    async def _main_spy(self, message: str) -> None:
        await self.message_queue.put({
            'type': 'acts-processor-message',
            'message': message,
        })

    def _create_spy(
            self,
            type_: str,
            issuer: str,
    ) -> T.Callable[[str], T.Awaitable[None]]:
        async def _spy(message: str) -> None:
            await self.message_queue.put({
                'type': type_,
                'issuer': issuer,
                'message': message,
            })

        return _spy

    async def _parse_acts_and_store_documents(
            self,
            issuer: str,
            parser: T.Callable[[T.Callable], T.Awaitable[T.Mapping[str, Act]]],
    ):
        parser_spy = self._create_spy('parser-message', issuer)
        storing_spy = self._create_spy('storing-message', issuer)
        docs_loader_spy = self._create_spy('docs-loader-message', issuer)

        await parser_spy('Collecting main acts data')
        acts = await parser(parser_spy)

        await storing_spy('Storing acts to the database')
        stored = {
            act.act_id: act
            for act in await API.fetch_acts(issuer=issuer)
        }

        await storing_spy('Storing main acts data')
        new_acts_stored = 0
        for act_id, act in acts.items():
            if act_id in stored:
                del stored[act_id]
            else:
                await API.create_act(act)
                new_acts_stored += 1
        if new_acts_stored:
            await storing_spy(f'{new_acts_stored} new acts stored')
        else:
            await storing_spy(f'No new acts stored')

        # If any of the previously stored acts was not found on the
        # current acts list - mark them as `removed`
        if stored:
            n = len(stored)
            await storing_spy(f'Marking {n} acts as removed')
            for act in stored.values():
                await API.change_act(act.id, removed_from_source=True)

        await docs_loader_spy('Download every missing document')
        docs_without_files = await API.fetch_documents(
            needs_file=1,
            issuer=issuer,
        )
        total = len(docs_without_files)
        await docs_loader_spy(f'Missing documents: {total}')

        for i, document in enumerate(docs_without_files, 1):
            await docs_loader_spy(f'Downloading {i} document out of {total}')
            async with aiohttp.ClientSession() as session:
                async with session.get(document.url, timeout=120) as response:
                    file_name = document.url.rsplit('/', 1)[1]
                    last_modified = response.headers.get('Last-Modified')
                    if last_modified is None:
                        lm_datetime = datetime.today()
                    else:
                        lm_datetime = datetime(*parsedate_tz(last_modified)[:6])
                    files = [('file', file_name, await response.read())]
                    await API.change_document(
                        document.id,
                        files=files,
                        last_modified=str(lm_datetime),
                    )
                    await asyncio.sleep(1)

        await docs_loader_spy(f'{total} documents downloaded')

    async def forward_the_docs(self):
        acts = await API.fetch_acts_to_forward()
        total = len(acts)
        await self._main_spy(f'{total} acts to forward')

        for i, act in enumerate(acts, 1):
            await self._main_spy(f'Forwarding {i} out of {total}')

            the_file_to_send = b''
            for file in act.files:
                try:
                    file_path = f'/api-data/{file}'
                    ft = filetype.guess_mime(file_path)
                    if ft is None:
                        content = textract.process(file_path, language='ukr')
                    elif ft == 'application/pdf':
                        _kwargs = {
                            'filename': '/code/passport.pdf',
                            'extension': 'pdf',
                            'language': 'ukr',
                        }
                        content = textract.process(**_kwargs)

                        # When a document is too short - probably it's a bunch
                        # of scanned paper sheets, so use tesseract
                        if len(content) < 100:
                            _kwargs['method'] = 'tesseract'
                            content = textract.process(**_kwargs)
                    else:
                        raise NotImplementedError

                except TypeError:
                    # Sometime textract fails
                    # https://github.com/deanmalmgren/textract/issues/261
                    logger.warning('textract failed to extract from %s', file)
                    continue
                the_file_to_send = b'.\n\n\n'.join((the_file_to_send, content))
            act.file_content = the_file_to_send[2:]

            await Interest.forward_act(act)
            await API.change_act(act.id, forwarded=True)

        await self._main_spy(f'{total} acts forwarded')

    async def do_the_job(self):
        futures = []
        for issuer, parser in self.parsers:
            documents_dir = pathlib.Path(f'/api-data/acts/{issuer}')
            documents_dir.mkdir(exist_ok=True, parents=True)
            futures.append(self._parse_acts_and_store_documents(issuer, parser))

        await asyncio.gather(*futures)
        # await self.forward_the_docs()
        await self.message_queue.put('done')
