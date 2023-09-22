import transport

socket = transport.ClientSocket('localhost')

socket.send('hello')

d = socket.receive()

print(d)

socket.close()