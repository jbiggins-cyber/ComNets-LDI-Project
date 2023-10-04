from protocol import Protocol
import transport

# socket = transport.ClientSocket('localhost')



# # client = Protocol('client')

# # client.transport.send('hello')

# # d = client.transport.receive()

# # print(d)

# socket.close()


try:
    socket = transport.ClientSocket('localhost')

    # exchange messages on this connection
    while True:
        socket.send(input())
        r = socket.receive()

    # todo handle timeout
    socket.close()

except KeyboardInterrupt:
    socket.close()
