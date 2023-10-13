import messenger
import sys
from rdt_protocol import RDTFactory

NUM_ARGS = 2
if (len(sys.argv) < NUM_ARGS):
    raise IndexError("Not enough input arguments specified!\n\n"\
                     "Please enter: python simple_client.py socket_type")
SOCK_TYPE = sys.argv[1]

try:
    m = messenger.ClientMessenger(sock_type=SOCK_TYPE, ip='localhost', rdt=RDTFactory.create("1.0"))

    print("Successfully started " + m.sock_type + " client")

    # exchange messages on this connection
    while True:
        data = input()
        if data == 'close':
            m.finish()
        else:
            m.send(data)
            r = m.receive()

            print("CLIENT: received [[" + r + "]]")

    # todo handle timeout
    m.finish()

except KeyboardInterrupt:
    m.finish()
