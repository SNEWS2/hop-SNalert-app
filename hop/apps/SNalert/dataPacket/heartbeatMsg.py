from dataclasses import dataclass

from . import SNEWSBase


@dataclass
class SNEWSHeartbeat(SNEWSBase):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    detector_id: str
    sent_time: str
    machine_time: str
    location: str
    status: str
    content: str
