from datetime import datetime
# noinspection PyPep8Naming
import typing as T

from pydantic import BaseModel


class Document(BaseModel):
    order: str
    url: str

    act: int = None
    file: str = None
    last_modified: datetime = None

    id: int = None
    created: datetime = None
    updated: datetime = None


class Act(BaseModel):
    issuer: str
    act_id: str
    title: str
    documents: T.List[Document]

    forwarded: bool = False
    removed_from_source: bool = False
    needs_inspection: bool = False
    comments: str = None

    id: int = None
    created: datetime = None
    updated: datetime = None
