import protocol
import transport

# socket = transport.ClientSocket('localhost')



# # client = Protocol('client')

# # client.transport.send('hello')

# # d = client.transport.receive()

# # print(d)

# socket.close()


try:
    p = protocol.ClientProtocol('localhost')

    # exchange messages on this connection
    while True:
        data = input()
        if data == 'close':
            p.finish()
        else:
            p.send(data)
        r = p.receive()

    # todo handle timeout
    p.finish()

except KeyboardInterrupt:
    p.finish()
