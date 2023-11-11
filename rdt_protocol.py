import select
import time
from math import ceil

from transport import *
import rdt_functionality
from transport import GenericSocket

REJECT_FIRST_TIME_FLAG = False

class RDTProtocolStrategy():
    """Different protocols use the Strategy pattern"""

    FLAGS = {"ACK": 0x01, "FIN": 0x02, "NACK": 0x04}
    PACKET_DATA_LEN = 20 # bytes -- todo change
    N_FLAG_HEXS  = 2
    N_SEQ_DIGITS = 4
    N_CHECKSUM_CHARS = rdt_functionality.BYTE_SIZE
    N_ERROR_CORRECTION_CHARS = (PACKET_DATA_LEN + 1) * rdt_functionality.BYTE_SIZE
    RECV_TIMEOUT = 2 # seconds

    def __init__(self, error_prob: float, error_num: int, burst: int):
        self.error_prob = error_prob
        self.error_num = error_num
        self.burst = burst

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


    def _split_data_into_packets(self, data: str, flags: int = 0x00) -> list[str]:
        """
        Split up a message by size
        This does the make_pkt() functionality
        """
        packet_list = []
        n_packets = ceil(len(data) / self.PACKET_DATA_LEN)

        for i in range(n_packets):
            data_idx = i*self.PACKET_DATA_LEN
            next_data = data[data_idx:min(data_idx+self.PACKET_DATA_LEN, len(data))]

            # seq = i+1 means that seq of last packet == total
            checksum = ''.join(rdt_functionality.generateUDPChecksum(next_data.encode('utf-8')))
            header_params = {"seq": i+1, "total": n_packets, "flags": flags, "check": checksum}
            header = self._create_header(header_params)
            next_packet = header + '\n' + next_data
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
    def create(rdt_ver: str, error_prob: float, error_num: int, burst: int) -> RDTProtocolStrategy:
        if rdt_ver == '1.0':
            return RDTProtocol_v1(error_prob, error_num, burst)
        elif rdt_ver == '2.0':
            return RDTProtocol_v2_0(error_prob, error_num, burst)
        elif rdt_ver == '2.1':
            return RDTProtocol_v2_1(error_prob, error_num, burst)
        elif rdt_ver == '2.2':
            return RDTProtocol_v2_2(error_prob, error_num, burst)
        elif rdt_ver == '3.0':
            return RDTProtocol_v3(error_prob, error_num, burst)
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

                # getting here means we've received data
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

    def send_fsm(self, socket: GenericSocket, data: str):
        packets_to_send: list[str] = self._split_data_into_packets(data)
        print("MSG: SEND: will send: \033[33m", packets_to_send, '\033[0m')
        for packet in packets_to_send:
            
            if data == "FINMSG":
                socket.send(packet)
                return
            else:
                corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                socket.send(corruptPkt)

            while True:
                receipt: str = socket.receive()
                header, data = self._extract(receipt)

                # if this condition hits, we have successful ACK
                if header["flags"] & self.FLAGS["ACK"]:
                    print("Received an ACK, " + ("done" if int(header["seq"]) == int(header["total"]) else "sending next packet"))
                    break

                # if this condition hits, we need to re-request
                if header["flags"] & self.FLAGS["NACK"]:
                    print("Received a NACK, retransmitting")
                    corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                    socket.send(corruptPkt)
                    continue
        return

    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        received_data_buffer = []
        have_received_data = False

        # This flag lets us deterministically fail the first transmission
        reject_first_time_flag = REJECT_FIRST_TIME_FLAG

        while True:
            receipt = socket.receive()
            header, data = self._extract(receipt)
            
            # fail the first transmission
            if reject_first_time_flag:
                reject_first_time_flag = False
                header["flags"] = self.FLAGS["NACK"]
                print(f"\033[31mNACKing packet #{header['seq']}\033[0m")
                socket.send(self._create_header(header))
                continue


            # print(list(header["check"]))
            checksum_valid = not rdt_functionality.verifyUDPChecksum(data.encode('utf-8'), list(header["check"]))

            # because this is RDT2.0, we make the assumption that the ACK is not affected by corruption
            if checksum_valid:
                received_data_buffer.append((header, data))
                header["flags"] = self.FLAGS["ACK"]
                print(f"ACKing packet #{header['seq']}")
                socket.send(self._create_header(header))
            elif not checksum_valid:
                header["flags"] = self.FLAGS["NACK"]
                print(f"\033[31mNACKing packet #{header['seq']}\033[0m")
                socket.send(self._create_header(header))
                continue

            if not have_received_data:
                expected_packets = int(header["total"])
                have_received_data = True
            if len(received_data_buffer) == expected_packets:
                return sorted(received_data_buffer, key=lambda r:r[0]["seq"])


class RDTProtocol_v2_1(RDTProtocol_v2_0):

    def _split_data_into_packets(self, data: str, flags: int = 0x00) -> list[str]:
        """
        Split up a message by size
        This does the make_pkt() functionality
        """
        packet_list = []
        n_packets = ceil(len(data) / self.PACKET_DATA_LEN)

        for i in range(n_packets):
            data_idx = i*self.PACKET_DATA_LEN
            next_data = data[data_idx:min(data_idx+self.PACKET_DATA_LEN, len(data))]

            # seq = i+1 means that seq of last packet == total
            error_correction_code = ''.join(map(str, rdt_functionality.generate2DParityCheck(next_data.encode('utf-8'))))
            header_params = {"seq": i+1, "total": n_packets, "flags": flags, "error_correction": error_correction_code}
            header = self._create_header(header_params)
            next_packet = header + '\n' + next_data
            packet_list.append(next_packet)

        return packet_list

    def _parse_header(self, header: str) -> dict[str, int]:
        """Take a header string and parse out the seq num, flags, (any other data we add in the future)"""
        i = header.index('S:')
        seq_num = int(header[i+len('S:'):i+self.N_SEQ_DIGITS+len('S:')])

        i = header.index('T:')
        total = int(header[i+len('T:'):i+self.N_SEQ_DIGITS+len('T:')])

        i = header.index('F:')
        flags = int(header[i+len('F:'):i+self.N_FLAG_HEXS+len('F:')])

        i = header.index('EC:')
        error_correction_code = header[i+len('EC:'):i+self.N_ERROR_CORRECTION_CHARS+len('EC:')]

        return {"seq": seq_num, "total": total, "flags": flags, "error_correction": error_correction_code}
    
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
        if not 'error_correction' in params:
            raise ValueError("Missing error correction code (key: 'error_correction')")
        return f"HEADER S:{params['seq']:04d} T:{params['total']:04d} F:{params['flags']:02x} EC:{params['error_correction'][0:self.N_ERROR_CORRECTION_CHARS]}"

    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        received_data_buffer = []
        have_received_data = False

        while True:
            receipt = socket.receive()
            header, data = self._extract(receipt)
            print(list(header["error_correction"]))
            data_encoded, error_correction_valid = rdt_functionality.verify2DParityCheck(data.encode('utf-8'), [int(bitChar) for bitChar in header["error_correction"]])
            data = data_encoded.decode('utf-8')

            # because this is RDT2.1, we make the assumption that the ACK is not affected by corruption
            if error_correction_valid:
                received_data_buffer.append((header, data))
                header["flags"] = self.FLAGS["ACK"]
                socket.send(self._create_header(header))
            elif not error_correction_valid:
                header["flags"] = self.FLAGS["NACK"]
                socket.send(self._create_header(header))

            if not have_received_data:
                expected_packets = int(header["total"])
                have_received_data = True
            if len(received_data_buffer) == expected_packets:
                return sorted(received_data_buffer, key=lambda r:r[0]["seq"])

class RDTProtocol_v2_2(RDTProtocolStrategy):
    pass

class RDTProtocol_v3(RDTProtocolStrategy):
    pass
