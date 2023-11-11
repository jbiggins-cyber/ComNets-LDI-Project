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
    PACKET_DATA_LEN = 20 # bytes (needs to be at least 3 bytes so ACK or NAK is in one packet)
    N_FLAG_HEXS  = 2
    N_SEQ_DIGITS = 4
    N_CHECKSUM_CHARS = rdt_functionality.BYTE_SIZE
    N_ERROR_CORRECTION_CHARS = (PACKET_DATA_LEN + 1) * rdt_functionality.BYTE_SIZE
    N_PKT_NUM_DIGITS = 1
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
            checksum = ''.join(rdt_functionality.generateUDPChecksum(next_data.encode('utf-8')))
            pkt_num = i % 2
            header_params = {"seq": i+1, "total": n_packets, "flags": flags, "check": checksum, "pkt_num": pkt_num}
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

        i = header.index('C:')
        checksum = header[i+len('C:'):i+self.N_CHECKSUM_CHARS+len('C:')]

        i = header.index('N:')
        pkt_num = header[i+len('N:'):i+self.N_PKT_NUM_DIGITS+len('N:')]

        return {"seq": seq_num, "total": total, "flags": flags, "check": checksum, "pkt_num": pkt_num}

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
        if not 'pkt_num' in params:
            raise ValueError("Missing packet number (key: 'pkt_num)")
        return f"HEADER S:{params['seq']:04d} T:{params['total']:04d} F:{params['flags']:02x} C:{params['check'][0:self.N_CHECKSUM_CHARS]} N:{params['pkt_num']:01d}"

    def send_fsm(self, socket: GenericSocket, data: str):
        packets_to_send: list[str] = self._split_data_into_packets(data)
        print("MSG: SEND: will send: \033[33m", packets_to_send, '\033[0m')

        for packet in packets_to_send:
            
            # always send close messages without corrupting them
            if data == "FINMSG":
                socket.send(packet)
                return
            
            # call to send pkt 0
            else:
                corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                socket.send(corruptPkt)

            # wait for ACK or NAK
            while True:
                receipt = socket.receive()
                header, data = self._extract(receipt)

                # if this condition hits, we have successful ACK
                if data == "ACK":
                    print("Received an ACK, " + ("done" if int(header["seq"]) == int(header["total"]) else "sending next packet"))
                    break

                # if this condition hits, we have successful NAK => need to re-request
                elif data == "NAK":
                    print("Received a NAK, re-sending packet")
                    corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                    socket.send(corruptPkt)

                # if this condition hits, we have garbled ACK/NAK => need to re-request
                else:
                    print("ACK/NAK was garbled, re-sending packet")
                    corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                    socket.send(corruptPkt)
        return
    
    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        received_data_buffer = []
        have_received_data = False

        recvSeqNum = 0      # receiver sequence number
        while True:
            receipt = socket.receive()
            header, data = self._extract(receipt)

            # checking FINMSG
            if data == "FINMSG":
                return [(header, data)]
            
            # saving expected number of packets
            if not have_received_data:
                expected_packets = int(header["total"])
                have_received_data = True

            # checking corrupt
            checksum_valid = not rdt_functionality.verifyUDPChecksum(data.encode('utf-8'), list(header["check"]))
            # send NAK if corrupt
            if not checksum_valid:
                print("Message corrupt, sending NAK")
                reply = (self._split_data_into_packets("NAK"))[0]

            # checking sequence number
            elif int(header["pkt_num"]) == recvSeqNum:
                # send ACK if correct sequence number, then update sequence number
                print("Sequence number correct, sending ACK and updating sequence number")
                received_data_buffer.append((header, data))
                reply = (self._split_data_into_packets("ACK"))[0]
                recvSeqNum = recvSeqNum ^ 1

                # must send uncorrupted ACK on last message received; Two Generals Problem
                if len(received_data_buffer) == expected_packets:
                    socket.send(reply)
                    return sorted(received_data_buffer, key=lambda r:r[0]["seq"])

            # wrong sequence number, need to re-send ACK
            else:
                print("Sequence number incorrect, re-sending ACK")
                reply = (self._split_data_into_packets("ACK"))[0]
            
            # sending ACK or NAK
            corruptReply = rdt_functionality.corruptPkt(reply, self.error_num, self.error_prob, self.burst)
            socket.send(corruptReply)

class RDTProtocol_v2_2(RDTProtocol_v2_1):

    def _split_data_into_packets(self, data: str, flags: int = 0x00, pkt_num_start=0) -> list[str]:
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
            pkt_num = (i+pkt_num_start) % 2
            header_params = {"seq": i+1, "total": n_packets, "flags": flags, "check": checksum, "pkt_num": pkt_num}
            header = self._create_header(header_params)
            next_packet = header + '\n' + next_data
            packet_list.append(next_packet)

        return packet_list
    
    def send_fsm(self, socket: GenericSocket, data: str):
        packets_to_send: list[str] = self._split_data_into_packets(data)
        print("MSG: SEND: will send: \033[33m", packets_to_send, '\033[0m')

        i = 0
        for packet in packets_to_send:

            if data == "FINMSG":
                socket.send(packet)
                return
            
            # call to send pkt 0
            else:
                corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                socket.send(corruptPkt)

                # getting current sequence number
                sndrSeqNum = i % 2

            # wait for ACK for correct pkt number
            while True:
                receipt = socket.receive()
                header, data = self._extract(receipt)

                # checking pkt number and successful ACK
                if (int(header["pkt_num"]) == sndrSeqNum) and (data == "ACK"):
                    print("Received an ACK, " + ("done" if int(header["seq"]) == int(header["total"]) else "sending next packet"))
                    i += 1
                    break
            
                # ACK is corrupted or for wrong sequence number => re-send
                else:
                    print("ACK garbled or for wrong packet, re-sending packet")
                    corruptPkt = rdt_functionality.corruptPkt(packet, self.error_num, self.error_prob, self.burst)
                    socket.send(corruptPkt)
                    continue
        return
    
    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        received_data_buffer = []
        have_received_data = False

        recvSeqNum = 0      # receiver sequence number
        while True:
            receipt = socket.receive()
            header, data = self._extract(receipt)

            # checking FINMSG
            if data == "FINMSG":
                return [(header, data)]

            # saving expected number of packets
            if not have_received_data:
                expected_packets = int(header["total"])
                have_received_data = True

            # checking corrupt
            checksum_valid = not rdt_functionality.verifyUDPChecksum(data.encode('utf-8'), list(header["check"]))
            # re-send ACK for previous packet if corrupt
            if not checksum_valid:
                print("Message corrupt, re-sending previous ACK")
                reply = (self._split_data_into_packets("ACK", pkt_num_start=(recvSeqNum^1)))[0]

            elif int(header["pkt_num"]) == recvSeqNum:
                # send ACK if correct sequence number, then update sequence number
                print("Sequence number correct, sending ACK and updating sequence number")
                received_data_buffer.append((header, data))
                reply = (self._split_data_into_packets("ACK", pkt_num_start=recvSeqNum))[0]
                recvSeqNum = recvSeqNum ^ 1

                # must send uncorrupted ACK on last message received; Two Generals Problem
                if len(received_data_buffer) == expected_packets:
                    socket.send(reply)
                    return sorted(received_data_buffer, key=lambda r:r[0]["seq"])
                
            # wrong sequence number, need to re-send ACK
            else:
                print("Sequence number incorrect, re-sending ACK")
                reply = (self._split_data_into_packets("ACK", pkt_num_start=(recvSeqNum^1)))[0]

            # sending ACK
            corruptReply = rdt_functionality.corruptPkt(reply, self.error_num, self.error_prob, self.burst)
            socket.send(corruptReply)

class RDTProtocol_v3(RDTProtocolStrategy):
    def send_fsm(self, socket: GenericSocket, data: str):
        packets_to_send: list[str] = self._split_data_into_packets(data)
        print("MSG: SEND: will send: \033[33m", packets_to_send, '\033[0m')

        for packet in packets_to_send:
            # poor way of getting the header value, but it'll do
            expected_ack_num =int(self._extract(packet)[0]["pkt_num"])
            
            # Don't wait for an ACK on a FINMSG, as we have the two generals problem
            if data == "FINMSG":
                socket.send(packet)
                return

            # wait for ACK
            while True:
                need_to_rerequest: bool = False 
                readable, _, _ = select.select([socket.sock], [], [], self.RECV_TIMEOUT)

                # check for timeout
                if not readable:
                    print("Timed out waiting for ACK, re-sending packet")
                    need_to_rerequest = True
                else:
                    receipt: str = socket.receive()
                    header, data = self._extract(receipt)
                    checksum_valid = not rdt_functionality.verifyUDPChecksum(data.encode('utf-8'), list(header["check"]))

                    # if this condition hits, we have successful ACK
                    if self._is_header_valid(header, expected_ack_num):
                        print("Received an ACK, " + ("done" if int(header["seq"]) == int(header["total"]) else "sending next packet"))
                        break
                    else:
                        print("Received duplicate/garbled ACK, re-sending packet")
                        need_to_rerequest = True
                    
                    if need_to_rerequest:
                        socket.send(packet)
                        continue
        return

    def _is_header_valid(self, header: dict[str, str], expected_ack_num: int) -> bool:
        """Determine if a header represents a valid packet"""
        return (header["flags"] & self.FLAGS["ACK"]) \
                and checksum_valid \
                and expected_ack_num == header["pkt_num"]

    def recv_fsm(self, socket: GenericSocket) -> list[tuple[str, str]]:
        pass
