from dataclasses import dataclass

from . import SNEWSBase


@dataclass
class SNEWSAlert(SNEWSBase):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    sent_time: str
    machine_time: str
    content: str
