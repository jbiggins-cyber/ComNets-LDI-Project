"""
This script runs the client side of the communications
It accepts socket type as an argument, which should preferrably be set to 'udp'

The server should start first so a binding is created
"""

import sys
import argparse

import messenger
from rdt_protocol import RDTFactory

parser = argparse.ArgumentParser(
    description="""This script runs the client side of the communications. The server should start first so a binding is created.""")
parser.add_argument('rdt_ver', choices=['1.0', '2.0', '2.1', '2.2', '3.0'],
                        help='RDT version (choose from: 1.0, 2.0, 2.1, 2.2, 3.0)')
parser.add_argument('--sock_type', choices=['udp', 'tcp'], default='udp',
                        help='Socket type (choose from: udp, tcp, default: udp)')
parser.add_argument('--ip', default='localhost',
                        help='IP address (default: localhost)')
parser.add_argument('--error_prob', default=0.0, type=float,
                        help='Probability of specified number of bit errors occuring in a message (default: 0.0)')
parser.add_argument('--error_num', default=1, type=int,
                        help='Number of random bit errors per message (default: 1)')
parser.add_argument('--burst', default=0, type=int,
                        help='Length of random burst error in every message (default: 0)')
args = parser.parse_args()

try:
    m = messenger.ClientMessenger(sock_type=args.sock_type, ip=args.ip, rdt=RDTFactory.create(args.rdt_ver, 
                                                                                                    args.error_prob, args.error_num, args.burst))

    print("Successfully started " + m.sock_type + " client")

    # exchange messages on this connection
    while True:
        data = input()

        if data == 'close':
            m.finish()
        else:
            print("Sending...")
            m.send(data)
            print("Waiting to receive...")
            r = m.receive()

            print("CLIENT: received [[" + r + "]]")

    # todo handle timeout
    m.finish()

except KeyboardInterrupt:
    m.finish()
