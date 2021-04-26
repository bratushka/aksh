import functools
# noinspection PyPep8Naming
import typing as T

import aiohttp

from structures import Act, Document


class BadResponse(Exception):
    pass


class Service:
    """Common parent for all services."""


class JSONAPI(Service):
    URL: str

    @classmethod
    async def _request(
            cls,
            method: str,
            path: str,
            *,
            params: dict = None,
            data: T.Any = None,
            files: T.List[T.Tuple[str, str, bytes]] = None,
            timeout: int = 3,
    ):
        stripped_path = path.strip('/')
        url = f'{cls.URL}/{stripped_path}/'

        # Remove params with a None value
        if params is not None:
            params = dict((k, v) for k, v in params.items() if v is not None)

        if files is None:
            data = aiohttp.JsonPayload(data)
        else:
            form = aiohttp.FormData()
            if data is not None and len(data) != 0:
                for k, v in data.items():
                    form.add_field(k, v)
            for field, file_name, file_bytes in files:
                form.add_field(field, file_bytes, filename=file_name)
            data = form

        async with aiohttp.ClientSession() as session:
            request = getattr(session, method)
            async with request(
                    url,
                    params=params,
                    data=data,
                    timeout=timeout,
            ) as response:
                if not response.ok:
                    raise BadResponse

                return await response.json()

    get: T.Callable = functools.partialmethod(_request, 'get')
    post: T.Callable = functools.partialmethod(_request, 'post')
    put: T.Callable = functools.partialmethod(_request, 'put')
    patch: T.Callable = functools.partialmethod(_request, 'patch')
    delete: T.Callable = functools.partialmethod(_request, 'delete')


class API(JSONAPI):
    # noinspection HttpUrlsUsage
    URL = 'http://api:8000'

    @classmethod
    async def fetch_acts(
            cls,
            **params
    ) -> T.List[Act]:
        results = await cls.get('acts/acts', params=params)

        return [Act(**r) for r in results]

    @classmethod
    async def create_act(cls, act: Act) -> Act:
        data = act.dict(
            exclude={'id', 'created', 'updated'},
            exclude_unset=True,
        )
        result = await cls.post('acts/acts', data=data)

        return Act(**result)

    @classmethod
    async def change_act(cls, pk: int, /, files=None, **data) -> Act:
        result = await cls.patch(f'acts/acts/{pk}', data=data, files=files)

        return Act(**result)

    @classmethod
    async def fetch_documents(cls, /, **params) -> T.List[Document]:
        results = await cls.get(f'acts/documents/', params=params)

        return [Document(**r) for r in results]

    @classmethod
    async def change_document(cls, pk: int, /, files=None, **data) -> Document:
        result = await cls.patch(f'acts/documents/{pk}', data=data, files=files)

        return Document(**result)
