from threading import Thread
from socketIO_client import SocketIO, LoggingNamespace
from radio_packet import RadioPacket


"""
A class which listens for events from a socket io endpoint, and spits our micro:bit shaped packets for the bridged micro:bit.
"""
class CloudVariableEp:

    socket = None
    connected = False
    changes = []

    """
    Constructor

    creates a socket, and background thread.

    Takes hub_variables (defined in hub.py) as a parameter for socket io ep address and port.
    """
    def __init__(self, hub_variables):
        self.socket = SocketIO(hub_variables["cloud_variable_socket"]["address"], hub_variables["cloud_variable_socket"]["port"])
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('reconnect', self.on_reconnect)
        self.socket.on('variable_changed', self.on_change)

        self.receive_events_thread = Thread(target=self._receive_events_thread)
        self.receive_events_thread.daemon = True
        self.receive_events_thread.start()

    """
    A callback when we successfully connect to a socket io ep

    TODO: use this state in emit logic.
    """
    def on_connect(self):
        self.connected = True

    """
    A callback when we are disconnected from a socket io ep

    TODO: use this state in emit logic.
    """
    def on_disconnect(self):
        self.connected = False

    """
    A callback when we are reconnected to a socket io ep

    TODO: use this state in emit logic.
    """
    def on_reconnect(self):
        self.connected = True

    """
    A callback when we receive a socket io event

    TODO: use this state in emit logic.
    """
    def on_change(self, msg):
        self.changes += [msg]

    """
    A background thread which listens for socket io events
    """
    def _receive_events_thread(self):
        self.socket.wait()

    """
    emit

    called by a driver, packets should resemble the following json structure:

    {
        "appId":int,
        "uid":int,
        "namespace":int,
        "variable_name":int,
        "value":string
    }
    """
    def emit(self,packet):
        self.socket.emit('variable_changed', packet)

    """
    drain

    Polled by the main application to get broadcast messages from the cloud variable ep.

    This class will asynchronously receive socket-based events from an endpoint and populate the changes array.
    """
    def drain(self):
        if self.changes == []:
            return ''

        if len(self.changes) == 1:
            head, changes = self.changes[0],[]
        else:
            head, changes = self.changes[0], self.changes[1:]

        # broadcast packet indicates we don't expect an ACK -- We've received this from a different hub.
        r = RadioPacket(None, head["appId"], head["uid"], RadioPacket.REQUEST_TYPE_CLOUD_VARIABLE | RadioPacket.REQUEST_TYPE_BROADCAST)
        r.append(head["namespace"])
        r.append(head["variable_name"])
        r.append(head["value"])

        self.changes = changes

        return r.marshall()
