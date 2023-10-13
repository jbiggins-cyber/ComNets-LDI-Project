import select
import time
from math import ceil

from transport import *

class RDTProtocolStrategy():
    """Different protocols use the Strategy pattern"""
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
        socket.send(data)

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
