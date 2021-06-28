from typing import List, AnyStr, Union
from uuid import UUID

import requests

from .models import Bucket, Object, NewObject


class Client:

    def __init__(self, base_url):
        self.base_url = base_url

    def buckets(self) -> List[Bucket]:
        r = requests.get(self.base_url + 'buckets')
        r.raise_for_status()

        return [Bucket(**b) for b in r.json()]

    def get(self, id: Union[AnyStr, UUID]) -> Object:
        r = requests.get(self.base_url + '/objects/{}'.format(id))
        r.raise_for_status()
        return Object(**r.json())

    def create(self, bucket, **kwargs) -> Object:
        new_obj = NewObject(bucket=bucket, **kwargs)
        r = requests.put(self.base_url + '/objects', data=new_obj.json(exclude_unset=True).encode())
        r.raise_for_status()
        return Object(**r.json())

    def finalize(self, obj: Object) -> Object:
        r = requests.post(self.base_url + '/objects/finalize', data=obj.json(exclude_unset=True).encode())
        r.raise_for_status()
        return Object(**r.json())
