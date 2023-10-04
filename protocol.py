from transport import *

class Protocol():
    def __init__(self, sock_type: str):
        transport_class = SocketFactory.new_socket(sock_type)
        self.transport = transport_class('localhost')

    def _send_chunk(self, next_chunk):
        self.transport.send(next_chunk)
        return self.transport.receive()
