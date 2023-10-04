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
        # there should be a better way to do this
        try:
            header_end = recv_buffer.index('\n')
            header = recv_buffer[:header_end]
            data = recv_buffer[header_end+1:]
        except ValueError:
            header = recv_buffer
            data = ""

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



#### TODO: THIS CLASS NEEDS A CLEANUP, A REVIEW OF API, AND PERHAPS A RENAMING
# IDEALLY, THERE WOULD BE SOME WAY FOR IT TO BE INTEGRATED INTO THE MESSENGER CLASS
# POTENTIALLY, ALL MESSENGER CLASS PACKETS COULD SUPPORT MOST OF THIS FUNCTIONALITY 
# THEMSELVES, AND IT'S UP TO THE PROTOCOL TO SELECT WHICH HEADERS TO USE. I'M UNSURE
# WHAT SHOULD BE DONE WITH THINGS LIKE THE ACK STATES, RETRANSMISSIONS, ETC.

class Protocol():

    FLAGS = {"ACK": 0x01, "FIN": 0x02, "NACK": 0x04}
    N_FLAG_HEXS  = 2
    N_SEQ_DIGITS = 4

    def __init__(self):
        self.seq = 0
        self.send_buffer = []

    def enqueue_packets(self, flags: int, data: str):
        """Split up a message by size and append the required headers"""
        data_idx = 0
        while len(data[data_idx:]) > PACKET_LEN:
            header_params = {"seq": self.seq, "flags": 0x00}
            next_packet = self.__create_header(header_params) + "\n" + data[data_idx:data_idx+self.PACKET_LEN]
            self.send_buffer.append(next_packet)
            
    def parse_packet(self, packet: str) -> tuple[dict[str, any], str]:
        """Parse a received packet into its params and data"""
        header, data = self.__get_header_data_split(packet)
        params = self.__parse_header(header)
        return params, data
    
    def __parse_header(self, header: str) -> dict[str, int]:
        """Take a header string and parse out the seq num, flags, (any other data we add in the future)"""
        i = header.index('S:')
        seq_num = int(header[i+len('S:'):i+self.N_SEQ_DIGITS+len('S:')])

        i = header.index('F:')
        flags = int(header[i+len('F:'):i+self.N_FLAG_HEXS+len('F:')])

        return {"seq": seq_num, "flags": flags}

    def __create_header(self, params: dict[str, any]) -> str:
        """Create the procotol header for given params
        Current params: `seq`, `flags`"""
        if not (0 <= params["seq"] <= 9999):
            raise ValueError(f"Seq num out of range: {seq}")
        if not (0x00 <= params["flags"] <= 0xFF):
            raise ValueError(f"Flags out of range: {flags}")
        return f"HEADER S:{params['seq']:04d} F:{params['flags']:02x}"

    def __get_header_data_split(self, buffer: str) -> tuple[str, str]:
        """Split a received buffer into header and data components"""
        try:
            header_end = buffer.index('\n')
            header = buffer[:header_end]
            data = buffer[header_end+1:]
        except ValueError:
            header = buffer
            data = ""

        return header, data
