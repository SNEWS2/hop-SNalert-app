from hop import plugins
from .dataPacket.observationMsg import SNEWSObservation
from .dataPacket.heartbeatMsg import SNEWSHeartbeat
from .dataPacket.alertMsg import SNEWSAlert

@plugins.register
def get_models():
    return {
        "snewsobservation": SNEWSObservation,
        "snewsheartbeat": SNEWSHeartbeat,
        "snewsalert": SNEWSHeartbeat
    }
