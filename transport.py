import socket

class SocketFactory():
    """Generator factory for one of the four socket types, being the mix of 'client'/'server' and 'tcp'/'udp'"""
    @staticmethod
    def new_socket(client_server: str, sock_type: str):
        if sock_type == 'tcp':
            if client_server == 'client':
                return ClientTCPSocket
            if client_server == 'server':
                return ServerTCPSocket
            raise ValueError("Invalid client/server type")
        elif sock_type == 'udp':
            if client_server == 'client':
                return ClientUDPSocket
            if client_server == 'server':
                return ServerUDPSocket
            raise ValueError("Invalid client/server type")
        raise ValueError("Invalid socket type")

class GenericSocket(): 
    """Generic socket that handles shared python socket API functions. 
    It presents a simplified API to the higher levels which our protocols can
    be implmented on top of.
    
    Generic Socket is the class that descendant TCP/UDP classes implement via polymorphism.
    Child classes will implement their own init, and override the send and receive methods.
    """

    """Default port for server to use, client will attempt to connect to this"""
    DEFAULT_PORT = 3000
    """Size of the default buffer to hold received data"""
    BUFFLEN = 1024

    def __init__(self, addr: str, sock_type: int = socket.SOCK_STREAM):
        self.opened = False # set in the child init!
        self.closed = False
        self.sock = socket.socket(socket.AF_INET, sock_type)
        self.binding = (addr, self.DEFAULT_PORT)
        self.sock.settimeout(1)

    def send(self, data: str):
        raise NotImplementedError()

    def receive(self) -> str:
        raise NotImplementedError()

    def close(self):
        """Close a socket"""
        if not self.opened:
            raise SocketNotOpenedError()
        if self.closed:
            raise ClosedSocketError()
        self.sock.close()
        print('closing socket')
        self.closed = True
        exit()

    def __del__(self):
        """ensure the socket is closed on garbage collection"""
        # check on openend ensures we actually had a connection in the first place
        if self.opened and not self.closed:
            self.close()


class TCPSocket(GenericSocket):
    """Parent class of the TCP Socket connections. Uses the SOCK_STREAM send and receive API"""
    def __init__(self, addr: str):
        super().__init__(addr, socket.SOCK_STREAM)
    
    def send(self, data: str):
        if self.closed:
            raise ClosedSocketError()
        self.sock.sendall(data.encode())
    
    def receive(self) -> str:
        """Wait for data to be received on the connection.
        If no data is received, the connection is closed"""
        # you can receive on a closed socket! -- Maybe have a TX closed and RX closed option?
        # if self.closed:
            # raise ClosedSocketError()
        data = self.sock.recv(self.BUFFLEN)
        if not data:
            self.close()
        return data.decode()


class ClientTCPSocket(TCPSocket):
    """Client socket to deal with client-specific TCP socket creation"""
    def __init__(self, addr: str):
        super().__init__(addr)
        # binding = (addr, self.DEFAULT_PORT)
        try:
            self.sock.connect(self.binding)
        except ConnectionRefusedError:
            print("Failed to start. Is the server running?")
            exit(1)
        self.opened = True

class ServerTCPSocket(TCPSocket):
    """Server socket to deal with server-specific TCP socket creation"""
    def __init__(self, addr: str):
        super().__init__(addr)
        # binding = (addr, self.DEFAULT_PORT)
        # allow the address to be reused when the next socket is created
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.binding)
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

class UDPSocket(GenericSocket):
    """Parent class of the UDP Socket connections. Uses the SOCK_DGRAM send and receive API"""
    def __init__(self, addr: str):
        super().__init__(addr, socket.SOCK_DGRAM)
    def send(self, data: str):
        self.sock.sendto(data.encode(), self.binding)
    def receive(self) -> str:
        return self.sock.recvfrom(self.BUFFLEN)[0].decode()

class ClientUDPSocket(UDPSocket):
    """Client socket to deal with client-specific UDP socket creation"""
    def __init__(self, addr: str):
        super().__init__(addr)
        self.opened = True

class ServerUDPSocket(UDPSocket):
    """Server socket to deal with server-specific UDP socket creation"""
    def __init__(self, addr: str):
        super().__init__(addr)
        self.sock.bind(self.binding)
        self.opened = True


class ClosedSocketError(Exception):
    """Raised when a user tries to send/receive on an already closed socket"""
    pass

class SocketNotOpenedError(Exception):
    """Raised when a user tries to close a socket that hasn't been opened"""
    pass
