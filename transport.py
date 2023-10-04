import socket

class SocketFactory():
    @staticmethod
    def new_socket(sock_type: str):
        if sock_type == 'client':
            return ClientSocket
        if sock_type == 'server':
            return ServerSocket
        raise ValueError("Invalid socket type")

class GenericSocket(): 
    """Generic socket that handles shared python socket API functions. 
    It presents a simplified API to the higher levels which our protocols can
    be implmented on top of.
    
    Currently uses TCP for ease of use but once the custom protocol is working,
    will switch to UDP.
    """

    """Size of the default buffer to hold received data"""
    DEFAULT_PORT = 3000
    BUFFLEN = 1024

    def __init__(self):
        self.opened = False # set in the child init!
        self.closed = False
        self._create_socket()

    def _create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)

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
        if not self.opened:
            raise SocketNotOpenedError()
        if self.closed:
            raise ClosedSocketError()
        self.sock.close()
        print('closing socket')
        self.closed = True

    def __del__(self):
        """ensure the socket is closed on garbage collection"""
        # check on openend ensures we actually had a connection in the first place
        if self.opened and not self.closed:
            self.close()


class ClientSocket(GenericSocket):
    """Client socket to deal with client-specific socket creation"""
    def __init__(self, addr: str):
        super().__init__()
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        binding = (addr, self.DEFAULT_PORT)
        try:
            self.sock.connect(binding)
        except ConnectionRefusedError:
            print("Failed to start. Is the server running?")
            exit(1)
        self.opened = True

class ServerSocket(GenericSocket):
    """Server socket to deal with server-specific socket creation"""
    def __init__(self, addr: str):
        super().__init__()
        binding = (addr, self.DEFAULT_PORT)
        # allow the address to be reused when the next socket is created
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(binding)
        self.sock.listen()

        # block until a connection arrives, then unblock
        while True:
            try:
                conn, info = self.sock.accept()
            except socket.timeout:
                pass
            except:
                raise
            else:
                self.sock = conn
                print("new connection on", info)
                self.opened = True
                return

class ClosedSocketError(Exception):
    """Raised when a user tries to send/receive on an already closed socket"""
    pass

class SocketNotOpenedError(Exception):
    """Raised when a user tries to close a socket that hasn't been opened"""
    pass
