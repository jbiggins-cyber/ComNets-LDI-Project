from datetime import datetime
import messenger

try:
    # make any number of connections until termination
    while True:
        m = messenger.ServerMessenger('localhost')

        # exchange messages on this connection
        while True:
            d = m.receive()
            print("received <<" + d + ">>")
            if d == "FINMSG" or d == "":
                print("closing because of receipt <<"+d+">>")
                m.finish()
                break
            elif d == 'drop':
                # drop this message
                pass
            # actual ack should be handled in the layers below, this is just the server response
            else:
                m.send('<<' + d + '>> rec\'d at ' + str(datetime.now()))
        # todo handle timeout

except KeyboardInterrupt:
    m.finish()
