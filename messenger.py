from transport import *
from rdt_protocol import *

# I think this needs to be changed somewhat
# once send is called, the whole Messenger API should block until the correct ACKs (or whatever the protocol dictates) have been received
# when receive is called, the API should block until we confirm that we have received the whole chunk desired.
#   Unsure how to have this call pend til then? Maybe the whole lower level will allow us to pend?



"""
messenger child classes need to define
- send (implement fsm)
- receive (implement fsm)
- _create_header
- _parse_header
"""

class Messenger():
    """The Messenger class manages communication using a custom designed protocol"""

    FLAGS = {"ACK": 0x01, "FIN": 0x02, "NACK": 0x04}
    N_FLAG_HEXS  = 2
    N_SEQ_DIGITS = 4
    N_CHECKSUM_CHARS = 7
    PACKET_DATA_LEN = 20 # bytes -- todo change

    def __init__(self, sock_type: str, ip: str):
        self.ip = ip
        # We hold the transport class so it can be used at any time to get a new socket of the right type
        self.__transport_class = SocketFactory.new_socket(sock_type)

    def _get_new_sock(self):
        self.transport = self.__transport_class(self.ip)

    def send(self, data: str):
        """Format this data with our own RDP protocol, then send over the lower-level base"""

        packets_to_send = self._split_data_into_packets(data)

        print("will send:", packets_to_send)

        for packet in packets_to_send:
            self.transport.send(packet)

    def receive(self):
        """Parse out the RDP protocol and just return our data"""
        recv_buffer = self.transport.receive()
        
        header, data = self.__get_header_data_split(recv_buffer)

        print("Received Messenger comms:\n" + "\tHeader: " + header + "\n\tData: " + data + "\n------")
        return data

    def finish(self):
        self.send("FINMSG")
        self.transport.close()

    def _split_data_into_packets(self, data: str) -> list[str]:
        """
        Split up a message by size
        This does the make_pkt() functionality
        """

        data_idx = 0
        packet_list = []
        seq = 0
        while len(data[data_idx:]) > self.PACKET_DATA_LEN:
            header_params = {"seq": seq, "flags": 0x00, "check": "abcdefg"}
            header = self._create_header(header_params)
            next_packet = header + '\n' + data[data_idx:min(data_idx+self.PACKET_DATA_LEN, len(data))]
            packet_list.append(next_packet)
            data_idx += self.PACKET_DATA_LEN
            seq += 1
        # todo fix indexing so we don't need to do again once the while loop finishes
        header_params = {"seq": seq, "flags": 0x00, "check": "abcdefg"}
        header = self._create_header(header_params)
        next_packet = header + '\n' + data[data_idx:min(data_idx+self.PACKET_DATA_LEN, len(data))]
        packet_list.append(next_packet)
        return packet_list

    def _extract(self, packet: str) -> tuple[dict[str, any], str]:
        """
        Parse a received packet into its params and data
        This is the extract() function
        """
        header, data = self.__get_header_data_split(packet)
        params = self._parse_header(header)
        return params, data


    # OVERRIDE IN CHILD 
    def _parse_header(self, header: str) -> dict[str, int]:
        """Take a header string and parse out the seq num, flags, (any other data we add in the future)"""
        i = header.index('S:')
        seq_num = int(header[i+len('S:'):i+self.N_SEQ_DIGITS+len('S:')])

        i = header.index('F:')
        flags = int(header[i+len('F:'):i+self.N_FLAG_HEXS+len('F:')])

        i = header.index('C:')
        checksum = int(header[i+len('F:'):i+self.N_CHECKSUM_CHARS+len('F:')])

        return {"seq": seq_num, "flags": flags, "check": checksum}

    # OVERRIDE IN CHILD
    def _create_header(self, params: dict[str, any]) -> str:
        """
        Create the procotol header for given params
        Current params: `seq`, `flags`, `check`
        """
        print(params)
        if not 'seq' in params:
            raise ValueError("Missing sequence number (key: 'seq')")
        if not (0 <= params["seq"] <= 9999):
            raise ValueError(f"Seq num out of range: {params['seq']}")
        if not 'flags' in params:
            raise ValueError("Missing flags (key: 'flags')")
        if not (0x00 <= params["flags"] <= 0xFF):
            raise ValueError(f"Flags out of range: {params['flags']}")
        if not 'check' in params:
            raise ValueError("Missing checksum (key: 'check')")
        # todo figure out checksum length! 7 is default git short length
        return f"HEADER S:{params['seq']:04d} F:{params['flags']:02x} C:{params['check'][0:self.N_CHECKSUM_CHARS]}"

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


class ClientMessenger(Messenger):
    def __init__(self, ip: str):
        super().__init__('client', ip)
        self._get_new_sock()

class ServerMessenger(Messenger):
    def __init__(self, ip:str):
        super().__init__('server', ip)
        self._get_new_sock()
