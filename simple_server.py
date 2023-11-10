"""
This script runs the server side of the communications
It accepts socket type as an argument, which should preferrably be set to 'udp'

This should start before the client so a binding is created
"""

from datetime import datetime
import sys
import argparse

import messenger
from rdt_protocol import RDTFactory

parser = argparse.ArgumentParser(
    description="""This script runs the server side of the communications. This should start before the client so a binding is created.""")
parser.add_argument('rdt_ver', choices=['1.0', '2.0', '2.1', '2.2', '3.0'],
                        help='RDT version (choose from: 1.0, 2.0, 2.1, 2.2, 3.0)')
parser.add_argument('--sock_type', choices=['udp', 'tcp'], default='udp',
                        help='Socket type (choose from: udp, tcp, default: udp)')
parser.add_argument('--ip', default='localhost',
                        help='IP address (default: localhost)')
parser.add_argument('--error_prob', default=0.0,
                        help='Probability of specified number of bit errors occuring in a message (default: 0.0)')
parser.add_argument('--error_num', default=1,
                        help='Number of random bit errors per message (default: 1)')
parser.add_argument('--burst', default=0,
                        help='Length of random burst error in every message (default: 0)')
args = parser.parse_args()

try:
    # make any number of connections until termination
    while True:
        m = messenger.ServerMessenger(sock_type=args.sock_type, ip=args.ip, rdt=RDTFactory.create(args.rdt_ver))

        print("Successfully started " + m.sock_type + " server")

        # exchange messages on this connection
        while True:
            print("Waiting to receive...")
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
                print("Sending...")
                m.send('<<' + d + '>> rec\'d at ' + str(datetime.now()))
        # todo handle timeout

except KeyboardInterrupt:
    m.finish()
