# ComNets-LDI-Project

This project contains the code used for the Communication Networks LDI project. The code creates a reliable data transport (RDT) protocol ontop of Python's `socket` library, with the ability to select from a number of different RDT versions.


## Code Design

A Static Design Diagram and System Sequence Diagram are shown below in `static_design_diagram.pdf` and `system_sequence_diagram.pdf` respectively.

## Usage
To set up client/server communications, simply enter one of the following commands:
```
python3 simple_server.py udp
python3 simple_client.py udp
```
From the client side, you can then type messages to send to the server. Note: start the server first, or the client won't have a binding to connect to.


The Messenger class and its subclasses provide the interface for the
application to use. Callers should instantiate either a `ClientMessenger` or `ServerMessenger`, and call the send, receive, and finish methods. The client should begin with send, while the server should begin with receive. Internal functions will break up the message into appropriate sized packets, and ensure its delivery.

The `ClientMessenger` and `ServerMessenger` classes act as a convenience classes, setting up the required variables.

The Socket classes are an interface to python's `socket` api It handles the different set up required for the client and server sides of the socket process. Additionally, it can handle both TCP and UDP comms. These are managed through the subclasses:

- `ClientTCPSocket`
- `ServerTCPSocket`
- `ClientUDPSocket`
- `ServerUDPSocket`

`GenericSocket`, `TCPSocket`, and `UDPSocket` are abstract classes, and shouldn't be
used directly by the user.

## Test scripts

`rdt_functionality_testing.py` runs tests on the conversion functionality of the checksums and binary encoding.

`checksum_performance_testing.py` runs a simulation of nearly 3 million messages for a variety of bit error quantities and burst error lengths, to determine the ability for the checksums to resolve errors in the incoming data.
