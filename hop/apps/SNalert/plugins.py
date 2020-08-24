from hop import plugins
from .dataPacket.observationMsg import ObservationMsg
from .dataPacket.heartbeatMsg import HeartbeatMsg

@plugins.register
def get_models():
    return {
        "observationMsg": ObservationMsg,
        "heartbeatMsg": HeartbeatMsg
    }