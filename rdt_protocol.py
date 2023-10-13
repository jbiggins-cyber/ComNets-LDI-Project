"""This file defines the different RDT protocols that we can use"""

class RDTProtocol():
    def __init__(self):
        pass
    def send_fsm(self, socket: GenericSocket, data: str):
        pass
    def recv_fsm(self, socket: genericSocket):
        pass


class RDTFactory():
    """Get the management class corresponding to a particular RDT version"""
    @staticmethod
    def create(rdt_ver: str) -> RDTProtocol:
        if rdt_ver == '1.0':
            return RDTProtocol_v1_0()
        elif rdt_ver == '2.0':
            return RDTProtocol_v2_0
        elif rdt_ver == '2.1':
            return RDTProtocol_v2_1
        elif rdt_ver == '2.2':
            return RDTProtocol_v2_2
        elif rdt_ver == '3.0':
            return RDTProtocol_v3
        else:
            raise ValueError("Invalid RDT version")


class RDTProtocol_v1(RDTProtocol):
    pass

class RDTProtocol_v2_0(RDTProtocol):
    pass

class RDTProtocol_v2_1(RDTProtocol):
    pass

class RDTProtocol_v2_2(RDTProtocol):
    pass

class RDTProtocol_v3(RDTProtocol):
    pass
