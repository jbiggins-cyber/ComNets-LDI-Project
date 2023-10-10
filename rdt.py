from math import ceil

BYTE_SIZE = 8

def str2Bin(message: str):
    # This function converts a string to a unicode array of bit characters.
    # (Unicode is commonly used to assign unique numbers to characters)
    # We need this function if we want to randomly corrupt the message,
    # or compute a checksum.

    # Initialising
    binArr = []

    # Converts string into bytes object
    unicodeMessage = message.encode('utf-8')

    # Convert each unique unicode byte representing a character into binary
    for uniqueVal in unicodeMessage:
        unicode = bin(uniqueVal)[2:]    # Need to ignore first two string elements '0b'
        while len(unicode) % 8:         # Need to add leading 0's to fill out bytes
            unicode = '0' + unicode
        for bit in unicode:
            binArr.append(bit)
    return binArr

def bin2Str(message: list):
    # This function converts a unicode binary of bit characters back to a string.
    # The binary array could potentially be corrupted.

    byteArr = bytearray()
    numBytes = ceil(len(message) / BYTE_SIZE)
    bitStr = ''.join(message)
    value = int(bitStr, 2)
    byteArr = value.to_bytes(numBytes)
    messageStr = byteArr.decode('utf-8')
        
    return messageStr

def bytes2Bin(payload: bytes):
    # This function converts the received payload from bytes into a unicode binary array.
    # We need this function to verify a checksum.

    raise NotImplementedError()

message = "This is a tϧst message string!"
print("Original message: {}".format(message))
unicodeMessage = str2Bin(message)
print("Message to binary: {}".format(''.join(unicodeMessage)))
decodedMessage = bin2Str(unicodeMessage)
print("Binary to string: {}".format(decodedMessage))