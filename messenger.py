"""
The Messenger class and its subclasses provide the interface for the
application to use.
Callers should instantiate either a ClientMessenger or ServerMessenger, and
call the send, receive, and finish methods. The client should begin with send,
while the server should begin with receive. Internal functions will break up
the message into appropriate sized packets, and ensure its delivery.

The ClientMessenger and ServerMessenger classes act as a convenience classes,
setting up the required variables.
"""

import select
import time
from math import ceil

from transport import *
from rdt_protocol import *

class Messenger():
    """The Messenger class manages communication using a custom designed protocol"""

    def __init__(self, client_server: str, sock_type: str, ip: str, rdt: RDTProtocolStrategy):
        self.sock_type: str = sock_type
        self.ip: str = ip
        # We hold the transport class so it can be used at any time to get a new socket of the right type
        self.__transport_class = SocketFactory.new_socket(client_server, sock_type)
        self.rdt = rdt

    def _get_new_sock(self):
        """instantiate a socket from the class"""
        self.transport: GenericSocket = self.__transport_class(self.ip)

    def send(self, data: str):
        """Break the data up into packets and then send via the RDT protocol"""
        self.rdt.send_fsm(self.transport, data)

    def receive(self) -> str:
        """Use our RDT protocol to receive data"""
        received_data: list[tuple[str, str]] = self.rdt.recv_fsm(self.transport)
        # For now, just return our data as a string
        return ''.join([r[1] for r in received_data])

    def finish(self):
        """Terminate a connection"""
        self.send("FINMSG")
        self.transport.close()


class ClientMessenger(Messenger):
    def __init__(self, sock_type: str, ip: str, rdt: RDTProtocolStrategy):
        super().__init__('client', sock_type, ip, rdt)
        self._get_new_sock()

class ServerMessenger(Messenger):
    def __init__(self, sock_type: str, ip: str, rdt: RDTProtocolStrategy):
        super().__init__('server', sock_type, ip, rdt)
        self._get_new_sock()
