from dataclasses import dataclass
import json

# import hop.models
from hop.models import MessageModel
from dataclasses_jsonschema import JsonSchemaMixin
from .dataPacketID import DataPacketID


@dataclass
class AlertMsg(MessageModel, JsonSchemaMixin):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    # header: dict
    # body: str
    message_id: str
    sent_time: str
    machine_time: str
    content: str

    @staticmethod
    def getID():
        return DataPacketID("AlertMsg")

    def __str__(self):
        return [(attribute.upper() + ":").ljust(9) + value for attribute, value in self.__dict__.items()]

    @classmethod
    def load(cls, input):
        """

        :param input: A serialized json string converted by asdict().
        :return:
        """

        # detector_name = input
        dict = json.loads(input)
        return cls(
            message_id=dict['message_id'],
            sent_time=dict['sent_time'],
            machine_time=dict['machine_time'],
            content=dict['content']
        )

    def getMessageID(self):
        return self.message_id

    def getSentTime(self):
        return self.sent_time

    def getMachineTime(self):
        return self.machine_time

    def getMsgContent(self):
        return self.content

