from enum import Enum

class P2PEvents(Enum):
    STARTED = 'started'
    CONNECTED = 'connected'
    MESSAGE_RECEIVED = 'message_received'
    DISCONNECTED = 'disconnected'
    SHUTDOWN = 'shutdown'