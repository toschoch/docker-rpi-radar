from pathlib import Path
import uuid
import json


class Object:

    def __init__(self, **kwargs):
        suffix = kwargs.pop("suffix", "")
        base_path = kwargs.pop("base_path", "/data")
        self.meta = kwargs
        self.id = uuid.uuid4()
        self.path = Path(base_path).joinpath(str(self.id)).with_suffix(suffix)

    @property
    def payload(self):
        p = self.meta.copy()
        p.update({"id": str(self.id), "path": str(self.path)})
        return p


class ObjectDB:
    base_path = Path('.')

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def new(self, **kwargs) -> Object:
        obj = Object(base_path=ObjectDB.base_path, **kwargs)
        self.mqtt.publish("store/objects/new", payload=json.dumps(obj.payload))
        return obj

    def created(self, obj: Object):
        self.mqtt.publish("store/objects/created", payload=json.dumps(obj.payload))

    def upload(self, obj: Object):
        self.mqtt.publish("store/objects/upload", payload=json.dumps(obj.payload))