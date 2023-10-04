import transport

try:
    # make any number of connections until termination
    while True:
        socket = transport.ServerSocket('localhost')

        # exchange messages on this connection
        while True:
            d = socket.receive()
            print("received <<" + d + ">>")
            if d == 'close' or d == "":
                print("closing because of receipt <<"+d+">>")
                # socket.send("FIN ACK")
                socket.close()
                break
            elif d == 'drop':
                # drop this message
                pass
            else:
                socket.send('ACK MSG <<' + d + '>>')
        # todo handle timeout

except KeyboardInterrupt:
    socket.close()
