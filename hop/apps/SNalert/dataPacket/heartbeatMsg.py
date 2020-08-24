from dataclasses import dataclass
import json

# import hop.models
from hop.models import MessageModel
from dataclasses_jsonschema import JsonSchemaMixin
from .dataPacketID import DataPacketID


@dataclass
class HeartbeatMsg(MessageModel, JsonSchemaMixin):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    # header: dict
    # body: str
    message_id: str
    detector_id: str
    sent_time: str
    machine_time: str
    location: str
    status: str
    content: str

    @staticmethod
    def getID():
        return DataPacketID("HeartbeatMsg")

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
            detector_id=dict['detector_id'],
            sent_time=dict['sent_time'],
            machine_time=dict['machine_time'],
            location=dict['location'],
            status=dict['status'],
            content=dict['content']
        )

    def getMessageID(self):
        return self.message_id

    def getDetectorID(self):
        return self.detector_id

    def getSentTime(self):
        return self.sent_time

    def getMachineTime(self):
        return self.machine_time

    def getLocation(self):
        return self.location

    def getStatus(self):
        return self.status

    def getMsgContent(self):
        return self.content

