import socket

class SocketFactory():
    @staticmethod
    def new_socket(sock_type: str, addr: str):
        if sock_type == 'client':
            return ClientSocket(addr)
        if sock_type == 'server':
            return ServerSocket(addr)
        raise ValueError("Invalid socket type")

class GenericSocket(): 
    """Generic socket that handles shared python socket API functions"""

    """Size of the default buffer to hold received data"""
    DEFAULT_PORT = 3000
    BUFFLEN = 1024

    def __init__(self):
        self._create_socket()
        self.closed = False

    def _create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, data: str):
        """Datastring to send along the connection"""
        if self.closed:
            raise ClosedSocketError()
        self.sock.sendall(data.encode())

    def receive(self) -> str:
        """Wait for data to be received on the connection.
        If no data is received, the connection is closed"""
        if self.closed:
            raise ClosedSocketError()
        data = self.sock.recv(self.BUFFLEN)
        if not data:
            self.close()
        return data.decode()

    def close(self):
        """Close a socket"""
        if self.closed:
            raise ClosedSocketError()
        self.sock.close()
        self.closed = True

    def __del__(self):
        """ensure the socket is closed on garbage collection"""
        if not self.closed:
            self.close()


class ClientSocket(GenericSocket):
    """Client socket to deal with client-specific socket creation"""
    def __init__(self, addr: str):
        super().__init__()
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        binding = (addr, self.DEFAULT_PORT)
        self.sock.connect(binding)

class ServerSocket(GenericSocket):
    """Server socket to deal with server-specific socket creation"""
    def __init__(self, addr: str):
        super().__init__()
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        binding = (addr, self.DEFAULT_PORT)
        self.sock.bind(binding)
        self.sock.listen()
        self.sock, addr = self.sock.accept()

class ClosedSocketError(Exception):
    """Raised when a user tries to send/receive on an already closed socket"""
    pass
