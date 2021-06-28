import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Status(str, Enum):
    created = 'created'
    written = 'written'


class ObjectMutable(BaseModel):
    date: Optional[datetime] = Field(None, example='2016-08-29T09:12:33.001Z')
    size: Optional[int] = Field(None, example=234233342)
    extension: Optional[str] = Field(None, example='mp4')
    mimetype: Optional[str] = Field(None, example='video/mp4')
    filename_template: Optional[str] = Field(
        None,
        description='template for the filename (gets automatically extended by { id }.{ extension })',
        example='{ date }',
    )
    meta: Optional[Dict[str, Any]] = Field(
        {},
        example={'size': {'width': 640, 'height': 480}, 'fps': 10, 'device': 'radarpi'},
    )


class NewObject(ObjectMutable):
    bucket: str = Field(..., example='videos')


class NewObjectToStore(NewObject):
    id: UUID = Field(..., example='d290f1ee-6c54-4b01-90e6-d701748f0851')
    status: Status = Field(..., example='created')
    extension: str = Field(..., example='mp4')

    @staticmethod
    def new(new_obj: NewObject):
        return NewObjectToStore(id=uuid.uuid4(),
                                status=Status.created,
                                created=datetime.utcnow(),
                                **new_obj.dict(exclude_unset=True))


class Object(NewObjectToStore):
    location: str = Field(
        None, example='/data/d290f1ee-6c54-4b01-90e6-d701748f0851.mp4'
    )
    created: datetime = Field(..., example='2016-08-29T09:12:33.001Z')


class ObjectUpdate(ObjectMutable):
    id: UUID = Field(..., example='d290f1ee-6c54-4b01-90e6-d701748f0851')


class MaxSizeQueueConfig(BaseModel):
    absolute: Optional[str] = Field(..., example="10G")
    extending: bool = Field(default=False, example='false')


class StorageConfig(BaseModel):
    max_size: Optional[MaxSizeQueueConfig] = Field(..., example={'absolute': '10G'})
    usual_object_size: str = Field('1M', example='1.4M')
    margin_size: str = Field('100M', example='1G')


class Bucket(BaseModel):
    name: str = Field(..., example='videos')
    mimetype: Optional[str] = Field(None, example='video/mp4')
    extension: Optional[str] = Field(None, example='mp4')
    filename_template: Optional[str] = Field(
        None,
        description='template for the filename (gets automatically extended by { id }.{ extension })',
        example='{{ date }}',
    )
    meta: Dict[str, Any] = Field(..., example={'device': 'radarpi'})
    storage: StorageConfig = Field(..., example={'maxsize': {'absolute': '10G'}})


def update_model(m1: BaseModel, m2: BaseModel, include) -> BaseModel:
    d = m2.dict(include=include)
    d.update(m1.dict(exclude_none=True))
    return type(m1)(**d)


def update_with_dict(m: BaseModel, updated) -> BaseModel:
    d = m.dict()
    if 'meta' in d and d['meta'] is not None and 'meta' in updated and updated['meta'] is not None:
        d['meta'].update(updated['meta'])
        updated['meta'] = d['meta']
    d.update(updated)
    return type(m)(**d)
