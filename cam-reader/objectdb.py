from pathlib import Path
import uuid
import json
import os
import shutil
import requests


class Object:

    def __init__(self, **kwargs):
        self.suffix = kwargs.pop("suffix", "")
        base_path = kwargs.pop("base_path", "/data")
        self.base_path = base_path
        self.meta = kwargs
        self.id = uuid.uuid4()
        self.path = Path(base_path).joinpath(str(self.id)).with_suffix(self.suffix)

    @property
    def payload(self) -> dict:
        p = self.meta.copy()
        p.update({"id": str(self.id), "path": str(self.path.relative_to(self.base_path))})
        return p


class ObjectDB:
    base_path = "http://localhost:8000"
    new_topic = "store/objects/new"
    finalized_topic = "store/objects/created"
    deleted_topic = "store/objects/deleted"

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def new(self, **kwargs) -> Object:
        r = requests.put(self.base_path + "/objects", json=kwargs)
        obj = r.json()
        self.mqtt.publish(self.new_topic, payload=json.dumps(obj), retain=False)
        return obj

    def rename(self, obj: Object, path_format_string: str = None, path_string_function=None):
        original_payload = obj.payload.copy()
        if path_format_string is not None:
            new_path_string = path_format_string.format(**obj.payload)
        else:
            new_path_string = path_string_function(obj.payload)
        new_path_string = new_path_string + "_" + str(obj.id)
        new_path = Path(self.base_path)\
            .joinpath(new_path_string)\
            .with_suffix(obj.suffix)
        os.makedirs(new_path.parent, exist_ok=True)
        shutil.move(obj.path, new_path)
        obj.path = new_path
        self.mqtt.publish(self.deleted_topic, payload=json.dumps(original_payload), retain=False)
        self.mqtt.publish(self.new_topic, payload=json.dumps(obj.payload), retain=False)

    def finalize(self, obj: dict):
        r = requests.post(self.base_path + "/objects/{}/finalize".format(obj['id']), json=obj)
        obj = r.json()
        self.mqtt.publish(self.finalized_topic, payload=json.dumps(obj), retain=False)

    def upload(self, obj: Object):
        self.mqtt.publish("store/objects/upload", payload=json.dumps(obj.payload), retain=False)
