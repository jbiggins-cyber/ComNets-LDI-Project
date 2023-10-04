import messenger

try:
    m = messenger.ClientMessenger('localhost')

    # exchange messages on this connection
    while True:
        data = input()
        if data == 'close':
            m.finish()
        else:
            m.send(data)
        r = m.receive()

    # todo handle timeout
    m.finish()

except KeyboardInterrupt:
    m.finish()
