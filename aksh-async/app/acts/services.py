import base64
import logging
# noinspection PyPep8Naming
import typing as T

from app.acts.structures import Act, ActToForward, Document
from app.core import services
from app.core.settings import INTERESTS_API_KEYS


logger = logging.getLogger(__name__)


class API(services.API):
    @classmethod
    async def fetch_acts(cls, **params) -> T.List[Act]:
        response = await cls.get('acts/acts/', params=params)
        if not response.ok:
            error_text = f'Error retrieving acts from {cls.URL}'
            raise services.ServiceException(error_text)

        return [Act(**a) for a in response.data]

    @classmethod
    async def create_act(cls, act: Act) -> Act:
        data = act.dict(
            exclude={'id', 'created', 'updated'},
            exclude_unset=True,
        )
        response = await cls.post('acts/acts/', data=data)
        if not response.ok:
            error_text = f'Error creating act {act.act_id}: {act.title}'
            raise services.ServiceException(error_text)

        return Act(**response.data)

    @classmethod
    async def change_act(cls, pk: int, /, files=None, **data) -> Act:
        response = await cls.patch(f'acts/acts/{pk}/', data=data, files=files)
        if not response.ok:
            error_text = f'Error changing act with pk={pk} in {cls.URL}'
            raise services.ServiceException(error_text)

        return Act(**response.data)

    @classmethod
    async def fetch_acts_to_forward(cls) -> T.List[ActToForward]:
        response = await cls.get('acts/acts-to-forward/', timeout=20)
        if not response.ok:
            error_text = f'Error retrieving acts to follow from {cls.URL}'
            raise services.ServiceException(error_text)

        return [ActToForward(**r) for r in response.data]

    @classmethod
    async def fetch_documents(cls, /, **params) -> T.List[Document]:
        response = await cls.get(f'acts/documents/', params=params)
        if not response.ok:
            error_text = f'Error retrieving documents from {cls.URL}'
            raise services.ServiceException(error_text)

        return [Document(**r) for r in response.data]

    @classmethod
    async def change_document(cls, pk: int, /, files=None, **data) -> Document:
        uri = f'acts/documents/{pk}/'
        response = await cls.patch(uri, data=data, files=files)
        if not response.ok:
            error_text = f'Error changing document with pk={pk} in {cls.URL}'
            raise services.ServiceException(error_text)

        return Document(**response.data)


class Interest(services.Interest):
    @classmethod
    async def forward_act(cls, act: ActToForward) -> None:
        headers = {'Authorization': INTERESTS_API_KEYS[act.issuer]}
        data = act.dict(include={'title', 'link', 'file_name', 'file_content'})
        data['file_content'] = base64.b64encode(data['file_content']).decode()
        data['file_name'] = data['file_name'] + '.txt'

        response = await cls.post(
            'api/document/push',
            headers=headers,
            data=data,
            timeout=10,
        )
        if not response.ok:
            logger.error(f'Error forwarding act #{act.id}')
            logger.error(f'Status: {response.status}')
            logger.error(f'Content: {str(response.data)}')
            error_text = f'Error forwarding act: {act.title}: {act.link}'
            raise services.ServiceException(error_text)
