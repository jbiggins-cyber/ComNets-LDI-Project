from datetime import datetime
import transport
import protocol

try:
    # make any number of connections until termination
    while True:
        p = protocol.ServerProtocol('localhost')

        # exchange messages on this connection
        while True:
            d = p.receive()
            print("received <<" + d + ">>")
            if d == 'close' or d == "":
                print("closing because of receipt <<"+d+">>")
                p.finish()
                break
            elif d == 'drop':
                # drop this message
                pass
            # actual ack should be handled in the layers below, this is just the server response
            else:
                p.send('<<' + d + '>> rec\'d at ' + str(datetime.now()))
        # todo handle timeout

except KeyboardInterrupt:
    p.finish()
