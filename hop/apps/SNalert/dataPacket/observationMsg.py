from dataclasses import dataclass

from . import SNEWSBase


@dataclass
class SNEWSObservation(SNEWSBase):
    """
    Defines an observation published by a detector.

    Formatted as a dictionary with the schema defined in the jsonSchema file.

    """
    detector_id: str
    sent_time: str
    neutrino_time: str
    machine_time: str
    location: str
    p_value: float
    status: str
    content: str
