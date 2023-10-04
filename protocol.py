from transport import *

class Protocol():
    def __init__(self, sock_type: str, ip: str):
        self.ip = ip
        # We hold the transport class so it can be used at any time to get a new socket of the right type
        self.__transport_class = SocketFactory.new_socket(sock_type)

    def get_new_sock(self):
        self.transport = self.__transport_class(self.ip)

    def send(self, data: str):
        """Format this data with our own RDP protocol, then send over the lower-level base"""
        send_buffer = "HEADER\n"+data+"\nFOOTER"
        self.transport.send(send_buffer)

    def receive(self):
        """Parse out the RDP protocol and just return our data"""
        recv_buffer = self.transport.receive()
        print("}}}" + recv_buffer + "{{{")
        # for now just remove HEADER and FOOTER
        return recv_buffer[len("HEADER\n"):-len("\nFOOTER")]

    def _send_chunk(self, next_chunk):
        self.transport.send(next_chunk)
        return self.transport.receive()


class ClientProtocol(Protocol):
    def __init__(self, ip: str):
        super().__init__('client', ip)
        self.get_new_sock()

class ServerProtocol(Protocol):
    def __init__(self, ip:str):
        super().__init__('server', ip)
        self.get_new_sock()

    