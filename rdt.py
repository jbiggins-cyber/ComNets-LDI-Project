from math import ceil

BYTE_SIZE =         8
BASE2 =             2

def str2Bin(message: str):
    # This function converts a string to a unicode list of bit characters.
    # (Unicode is commonly used to assign unique numbers to characters)
    # We need this function if we want to randomly corrupt the message,
    # or compute a checksum.

    # Initialising
    binList = []

    # Converts string into bytes object
    unicodeMessage = message.encode('utf-8')

    # Convert each unique unicode byte representing a character into binary
    for uniqueVal in unicodeMessage:
        unicode = bin(uniqueVal)[2:]            # Ignores first two string elements '0b'
        while len(unicode) % BYTE_SIZE:         # Adds leading 0's to fill out bytes
            unicode = '0' + unicode
        for bit in unicode:
            binList.append(bit)
    return binList

def bin2Str(message: list):
    # This function converts a unicode list of bit characters back to a message string.
    # The binary list could potentially be corrupted.

    byteList = bytearray()
    numBytes = ceil(len(message) / BYTE_SIZE)
    bitStr = ''.join(message)
    value = int(bitStr, BASE2)
    byteList = value.to_bytes(numBytes)
    messageStr = byteList.decode('utf-8')
        
    return messageStr

def bytes2Bin(payload: bytes):
    # This function converts the received payload from bytes into a unicode list of bit characters.
    # We need this function to verify a checksum.



    raise NotImplementedError()

message = "This is a tϧst message string!"
print("Original message: {}".format(message))
unicodeMessage = str2Bin(message)
print("Message to binary: {}".format(''.join(unicodeMessage)))
decodedMessage = bin2Str(unicodeMessage)
print("Binary to string: {}".format(decodedMessage))