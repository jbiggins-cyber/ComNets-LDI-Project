# ComNets-LDI-Project

This project contains the code used for the Communication Networks LDI project. The code creates a reliable data transport (RDT) protocol ontop of Python's `socket` library, with the ability to select from a number of different RDT versions.


## Code Design

A Static Design Diagram and System Sequence Diagram are shown below in `static_design_diagram.pdf` and `system_sequence_diagram.pdf` respectively.

## Usage
To set up client/server communications, simply enter one of the following commands, or use Docker as shown later.
```
python3 simple_server.py $rdt_ver
python3 simple_client.py $rdt_ver
```
From the client side, you can then type messages to send to the server. Note: start the server first, or the client won't have a binding to connect to.

`rdt_ver` is in `{1.0,2.0,2.1,2.2,3.0}`. The options to the script are 
```
-h, --help              show this help message and exit
--sock_type {udp,tcp}   Socket type (choose from: udp, tcp, default: udp)
--ip IP                 IP address (default: localhost)
```

### Structure

The Messenger class and its subclasses provide the interface for the
application to use. Callers should instantiate either a `ClientMessenger` or `ServerMessenger`, and call the send, receive, and finish methods. The client should begin with send, while the server should begin with receive. Internal functions will break up the message into appropriate sized packets, and ensure its delivery.

The `ClientMessenger` and `ServerMessenger` classes act as a convenience classes, setting up the required variables.

The Socket classes are an interface to python's `socket` api. They handle the different set up required for the client and server sides of the socket process. Additionally, it can handle both TCP and UDP comms. These are managed through the subclasses:

- `ClientTCPSocket`
- `ServerTCPSocket`
- `ClientUDPSocket`
- `ServerUDPSocket`

`GenericSocket`, `TCPSocket`, and `UDPSocket` are abstract classes, and shouldn't be
used directly by the user.

## Test scripts

`rdt_functionality_testing.py` runs tests on the conversion functionality of the checksums and binary encoding.

`checksum_performance_testing.py` runs a simulation of nearly 3 million messages for a variety of bit error quantities and burst error lengths, to determine the ability for the checksums to resolve errors in the incoming data.

## Using Docker

The client and server can also be launched using Docker. To do so, you will need to start one container for each. In separate terminals, type:
```
./docker_tools.sh build server
./docker_tools.sh run server
```
```
./docker_tools.sh build client
./docker_tools.sh run client
```

After making changes to code, you will need to rebuild the images.

The Docker containers are removed automatically. To remove the network, use 
```
./docker_tools.sh cleanup
```

## Using Docker and GNS3

### Exporting images

When the above Docker steps have been followed, images can be pushed to dockerhub like
```
docker tag rdt-client adleris/rdt-client
docker push adleris/rdt-client
```

### Pulling images into GNS3

Get the images:

- Open a GNS3 project
- *edit* > *preferences* > *docker containers*
- *new* > *new image* > "adleris/rdt-client" (or server) 
- accept name > 1 adaptor
- *start command* = `bash`
- *next* > *finish*

Configure the topology:

- From the *End Devices* panel, drag the images into the topology, along with a switch and router
- Start the router and configure it as per workshop 2
- Right click on each image, *Edit config* and assign a static IP eg 192.168.0.2
- Restart the network
- Open a console for each image
- Enter `python simple_client.py 1.0 --ip 192.168.0.2`, adjusting as required
- Enjoy communications!
