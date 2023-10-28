"""
This script runs the server side of the communications
It accepts socket type as an argument, which should preferrably be set to 'udp'

This should start before the client so a binding is created
"""

from datetime import datetime
import messenger
import sys

from rdt_protocol import RDTFactory

NUM_ARGS = 2
if (len(sys.argv) < NUM_ARGS):
    raise IndexError("Not enough input arguments specified!\n\n"\
                     "Please enter: python simple_server.py socket_type")
SOCK_TYPE = sys.argv[1]

try:
    # make any number of connections until termination
    while True:
        m = messenger.ServerMessenger(sock_type=SOCK_TYPE, ip='localhost', rdt=RDTFactory.create("2.0"))

        print("Successfully started " + m.sock_type + " server")

        # exchange messages on this connection
        while True:
            d = m.receive()
            print("SERVER: received <<" + d + ">>")
            if d == "FINMSG" or d == "":
                print("SERVER: closing because of receipt <<"+d+">>")
                m.finish()
                break
            elif d == 'drop':
                # drop this message
                pass
            # actual ack should be handled in the layers below, this is just the server response
            else:
                m.send('<<' + d + '>> rec\'d at ' + str(datetime.now()))
        # todo handle timeout

except KeyboardInterrupt:
    m.finish()
