from transport import *

class Messenger():
    """The Messenger class manages communication using a custom designed protocol"""

    def __init__(self, sock_type: str, ip: str):
        self.ip = ip
        # We hold the transport class so it can be used at any time to get a new socket of the right type
        self.__transport_class = SocketFactory.new_socket(sock_type)

    def get_new_sock(self):
        self.transport = self.__transport_class(self.ip)

    def send(self, data: str):
        """Format this data with our own RDP protocol, then send over the lower-level base"""
        send_buffer = "HEADER D1 D2 D3\n"+data
        self.transport.send(send_buffer)

    def receive(self):
        """Parse out the RDP protocol and just return our data"""
        recv_buffer = self.transport.receive()
        
        # in the first draft, header will be separated from data by a newline
        header_end = recv_buffer.index('\n')
        header = recv_buffer[:header_end]
        data = recv_buffer[header_end+1:]

        print("Received Messenger comms:\n" + "\tHeader: " + header + "\n\tData: " + data + "\n------")
        return data

    def _send_chunk(self, next_chunk):
        self.transport.send(next_chunk)
        return self.transport.receive()

    def finish(self):
        self.send("FINMSG")
        self.transport.close()

class ClientMessenger(Messenger):
    def __init__(self, ip: str):
        super().__init__('client', ip)
        self.get_new_sock()

class ServerMessenger(Messenger):
    def __init__(self, ip:str):
        super().__init__('server', ip)
        self.get_new_sock()

    