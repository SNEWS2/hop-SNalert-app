==========
Messages
==========

.. contents::
   :local:


SNEWS Custom Messages
----------------------

SNEWS 2.0 makes use of the fact that hop-client module supports
adding custom message formats as plugins. The base class SNEWSBase
inherits hop-client's external message model. For documentation
hop-client custom message plugins, see https://hop-client.readthedocs.io/en/latest/user/models.html.
SNEWSBase contains the field "message_id" for the purpose of recording
and tracing messages for SNEWS usage.

The abstract parent class is defined as

.. code:: python

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

        def __str__(self):
            return [(key.upper() + ":").ljust(9) + value for key, value in self.asdict().items()]

The dataclass SNEWSBase is equivalently defined with the constructor

.. code:: python

    class SNEWSBase(MessageModel, JsonSchemaMixin):
        def __init__(message_id: str)
            self.message_id = message_id


Obsevation Mesage
^^^^^^^^^^^^^^^^^^

On top of SNEWSBase, an observation message is sent by a detector upon observation
possible pre-supernova phenomenon. The observation message has the following additional attributes

    * detector_id: a unique string id of the detector
    * sent_time: the string format of the sending time of the message
    * neutrino_time: the string format of the neutrino time recording by the detector
    * machine_time: the string format of the machine time of the detector
    * location: a string of the location of the detector
    * p_value: a number indicating the P value of the observation
    * status: "ON" or "OFF" indicating the status of the detector
    * content: a string of any additional information of this observation

These attributes are required when a detector constructs a new observation message.
An observation message is initialized by

.. code-block::

    SNEWSObservation(
            message_id=,
            detector_id=,
            sent_time=,
            neutrino_time=,
            machine_time=,
            location=,
            p_value=,
            status=,
            content=,
        )

with alert messages and heartbeat messages alike.

Alert Message
^^^^^^^^^^^^^^

When SNEWS 2.0 determines that a possible supernova is about to happen, it sends
an alert message to all experiment detectors with optional instructions. An alert message
has the following attributes:

    * sent_time: a unique string id of the detector
    * machine_time: the string format of the machine time of the detector
    * content: a string of any additional information of this observation

Heartbeat Message
^^^^^^^^^^^^^^^^^^

All detectors regularly publishes heartbeat messages to tell
SNEWS 2.0 server that they are online. A heartbeat message consists of the attributes:

    * detector_id: a unique string id of the detector
    * sent_time: the string format of the sending time of the message
    * machine_time: the string format of the machine time of the detector
    * location: a string of the location of the detector
    * status: "ON" or "OFF" indicating the status of the detector
    * content: a string of any additional information of this observation


