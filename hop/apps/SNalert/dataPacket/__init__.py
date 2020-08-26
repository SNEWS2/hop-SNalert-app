from dataclasses import dataclass
import json

from hop.models import MessageModel
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class SNEWSBase(MessageModel, JsonSchemaMixin):
    """
    Defines a base SNEWS message type.

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
