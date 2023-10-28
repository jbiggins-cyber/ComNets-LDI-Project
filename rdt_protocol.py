import select
import time
from math import ceil

from transport import *

class RDTProtocolStrategy():
    """Different protocols use the Strategy pattern"""

    FLAGS = {"ACK": 0x01, "FIN": 0x02, "NACK": 0x04}
    N_FLAG_HEXS  = 2
    N_SEQ_DIGITS = 4
    N_CHECKSUM_CHARS = 7
    PACKET_DATA_LEN = 20 # bytes -- todo change
    RECV_TIMEOUT = 2 # seconds

    def __init__(self):
        pass

    def send_fsm(self, socket: GenericSocket, data: str):
        """
        send data using the RDT protocol
        """
        raise NotImplementedError()

    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        """
        Run the RDT protocol's receive FSM. Returns data in the form
        [
            (header1, data1),
            (header2, data2),
            ...
            (headerN, dataN)
        ]
        """
        raise NotImplementedError()


    def _split_data_into_packets(self, data: str) -> list[str]:
        """
        Split up a message by size
        This does the make_pkt() functionality
        """
        packet_list = []
        n_packets = ceil(len(data) / self.PACKET_DATA_LEN)

        for i in range(n_packets):
            data_idx = i*self.PACKET_DATA_LEN
            # insert checksum here!
            # seq = i+1 means that seq of last packet == total
            header_params = {"seq": i+1, "total": n_packets, "flags": 0x00, "check": "abcdefg"}
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

        i = header.index('T:')
        total = int(header[i+len('T:'):i+self.N_SEQ_DIGITS+len('T:')])

        i = header.index('F:')
        flags = int(header[i+len('F:'):i+self.N_FLAG_HEXS+len('F:')])

        i = header.index('C:')
        checksum = header[i+len('C:'):i+self.N_CHECKSUM_CHARS+len('C:')]

        return {"seq": seq_num, "total": total, "flags": flags, "check": checksum}

    # OVERRIDE IN CHILD
    def _create_header(self, params: dict[str, any]) -> str:
        """
        Create the procotol header for given params
        Current params: `seq`, `flags`, `check`
        """
        print("MSG: _create_header: params:",params)
        if not 'seq' in params:
            raise ValueError("Missing sequence number (key: 'seq')")
        if not (0 <= params["seq"] <= 9999):
            raise ValueError(f"Seq num out of range: {params['seq']}")
        if not 'total' in params:
            raise ValueError("Missing sequence number (key: 'total')")
        if not (0 <= params["total"] <= 9999):
            raise ValueError(f"Seq num out of range: {params['total']}")
        if not 'flags' in params:
            raise ValueError("Missing flags (key: 'flags')")
        if not (0x00 <= params["flags"] <= 0xFF):
            raise ValueError(f"Flags out of range: {params['flags']}")
        if not 'check' in params:
            raise ValueError("Missing checksum (key: 'check')")
        # todo figure out checksum length! 7 is default git short length
        return f"HEADER S:{params['seq']:04d} T:{params['total']:04d} F:{params['flags']:02x} C:{params['check'][0:self.N_CHECKSUM_CHARS]}"

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


class RDTFactory():
    """Get the management class corresponding to a particular RDT version"""
    @staticmethod
    def create(rdt_ver: str) -> RDTProtocolStrategy:
        if rdt_ver == '1.0':
            return RDTProtocol_v1()
        elif rdt_ver == '2.0':
            return RDTProtocol_v2_0()
        elif rdt_ver == '2.1':
            return RDTProtocol_v2_1()
        elif rdt_ver == '2.2':
            return RDTProtocol_v2_2()
        elif rdt_ver == '3.0':
            return RDTProtocol_v3()
        else:
            raise ValueError("Invalid RDT version")


class RDTProtocol_v1(RDTProtocolStrategy):
    def send_fsm(self, socket: GenericSocket, data: str):
        packets_to_send: list[str] = self._split_data_into_packets(data)
        print("MSG: SEND: will send: \033[33m", packets_to_send, '\033[0m')
        for packet in packets_to_send:
            socket.send(packet)

    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        """
        Run the RDT protocol's receive FSM. Returns data in the form
        [
            (header1, data1),
            (header2, data2),
            ...
            (headerN, dataN)
        ]
        """
        received_data_buffer = []

        have_received_data = False
        start_time = time.time()
        while True:
            time.sleep(1)
            remaining_timeout = self.RECV_TIMEOUT - (time.time() - start_time)
            
            more_data = select.select([socket.sock], [], [], self.RECV_TIMEOUT)
            # this check sees if there's any more data to be read on the socket
            # if we have read previously in this loop, then we're within the receipt state machine, and no data means we're done
            # if we've never read anything, then we are a server pending on a new receipt from the client, and so we just keep looping
            # print(more_data)

            if more_data[0] or remaining_timeout > 0:

                # getting here mean we've received data
                # print('more to receive')

                recv_buffer = socket.receive()
                if not have_received_data:
                    print("MSG: RCV: Received Messenger comms:")
                have_received_data = True
                header_params, data = self._extract(recv_buffer)

                print("Header: \033[31m" + str(header_params) + "\033[0m\nData: [\033[32m" + data + "\033[0m]\n------")

                received_data_buffer.append((header_params, data))

                # if we have the number of packets we need, we're done
                if len(received_data_buffer) == received_data_buffer[0][0]["total"]:
                    # sort the packets in order and pass up to caller
                    return sorted(received_data_buffer, key=lambda r:r[0]["seq"])


class RDTProtocol_v2_0(RDTProtocolStrategy):
    pass

class RDTProtocol_v2_1(RDTProtocolStrategy):
    pass

class RDTProtocol_v2_2(RDTProtocolStrategy):
    pass

class RDTProtocol_v3(RDTProtocolStrategy):
    pass
