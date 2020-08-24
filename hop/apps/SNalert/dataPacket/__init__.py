from dataclasses import dataclass
import json

from hop.models import MessageModel
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class SNEWSBase(MessageModel, JsonSchemaMixin):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    message_id: str

    @classmethod
    def load(cls, input_):
        """

        :param input: A serialized json string converted by asdict().
        :return:
        """
        if hasattr(input_, 'read'):
            payload = json.load(input_)
        else:
            payload = json.loads(input_)
        return cls(**payload)

    def __str__(self):
        return [(key.upper() + ":").ljust(9) + value for key, value in self.asdict().items()]
