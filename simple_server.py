import transport

socket = transport.ServerSocket('localhost')

d = socket.receive()
print(d)

socket.send('thanks')

socket.close()