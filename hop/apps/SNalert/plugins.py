from hop import plugins
from .dataPacket.observationMsg import ObservationMsg
from .dataPacket.heartbeatMsg import HeartbeatMsg
from .dataPacket.alertMsg import AlertMsg

@plugins.register
def get_models():
    return {
        "observationMsg": ObservationMsg,
        "heartbeatMsg": HeartbeatMsg,
        "alertMsg": AlertMsg
    }