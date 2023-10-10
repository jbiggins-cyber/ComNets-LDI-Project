from math import ceil

BYTE_SIZE =         8
BASE2 =             2

def str2Bin(message: str):
    # This function converts a string to a unicode list of bit characters.
    # (Unicode is commonly used to assign unique numbers to characters)
    # We need this function if we want to randomly corrupt the message,
    # or compute a checksum.

    # Converts string into bytes object using utf-8 encoding
    unicodeMessage = message.encode('utf-8')

    return bytes2Bin(unicodeMessage)

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

    # Initialising
    binList = []

    # Convert each unique unicode representing a character into binary
    for uniqueVal in payload:
        unicode = bin(uniqueVal)[2:]            # Ignores first two string elements '0b'
        while len(unicode) % BYTE_SIZE:         # Adds leading 0's to fill out bytes
            unicode = '0' + unicode
        for bit in unicode:
            binList.append(bit)
    return binList

print()
message = "This is a tϧst message string!"
print("Original message: {}".format(message))
unicodeMessage = str2Bin(message)
print("Message to binary: {}".format(''.join(unicodeMessage)))
decodedMessage = bin2Str(unicodeMessage)
print("Binary to string: {}".format(decodedMessage))

print()
byteArr = message.encode('utf-8')
print("Original message to bytes: {}".format(byteArr))
unicodeBytes = bytes2Bin(byteArr)
print("Bytes to binary: {}".format(''.join(unicodeBytes)))
decodedBytesMessage = bin2Str(unicodeBytes)
print("Decoded bytes payload: {}".format(decodedBytesMessage))