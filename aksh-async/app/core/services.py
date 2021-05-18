import dataclasses
import functools
import logging
# noinspection PyPep8Naming
import typing as T

import aiohttp


logger = logging.getLogger(__name__)


ReqType = T.Callable[..., T.Awaitable['ServiceResponse']]


@dataclasses.dataclass(frozen=True)
class ServiceResponse:
    ok: bool
    status: int
    data: T.Any
    type: T.Literal['text', 'json']


class ServiceException(Exception):
    pass


class Service:
    """Common parent for all services."""
    ServiceException = ServiceException


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
            headers: T.Mapping[str, str] = None,
            timeout: int = 3,
    ) -> ServiceResponse:
        stripped_path = path.lstrip('/')
        url = f'{cls.URL}/{stripped_path}'

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

        async with aiohttp.ClientSession(raise_for_status=False) as session:
            request = getattr(session, method)
            response: aiohttp.ClientResponse
            async with request(
                    url,
                    params=params,
                    data=data,
                    headers=headers,
                    timeout=timeout,
            ) as response:
                if not response.ok:
                    # noinspection PyProtectedMember
                    response.content._exception = None
                    if response.status < 500:
                        return ServiceResponse(
                            ok=False,
                            status=response.status,
                            data=await response.json(),
                            type='json',
                        )
                    else:
                        return ServiceResponse(
                            ok=False,
                            status=response.status,
                            data=await response.text(),
                            type='text',
                        )

                return ServiceResponse(
                    ok=True,
                    status=response.status,
                    data=await response.json(),
                    type='json',
                )

    get: ReqType = functools.partialmethod(_request, 'get')
    post: ReqType = functools.partialmethod(_request, 'post')
    put: ReqType = functools.partialmethod(_request, 'put')
    patch: ReqType = functools.partialmethod(_request, 'patch')
    delete: ReqType = functools.partialmethod(_request, 'delete')


class API(JSONAPI):
    # noinspection HttpUrlsUsage
    URL = 'http://api:8000'


class Interest(JSONAPI):
    # noinspection SpellCheckingInspection
    URL = 'https://interes.shtab.net'
