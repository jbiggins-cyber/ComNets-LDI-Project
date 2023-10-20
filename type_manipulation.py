from math import ceil

BYTE_SIZE =         8
BASE2 =             2
BASE10 =            10
SEED =              1083430
FAIL =              True
SUCCESS =           False

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

def bin2Bytes(unicodeBits: list):
    # This function converts the unicode list of bit characters into a Python bytearray.
    # We need this to check if the message has been successfully corrupted, because 
    # randomly corrupting the unicode may lead to the decode() function not working.

    # Initialising
    localUnicodeBits = unicodeBits[:]
    byteMessage = bytearray()
    currentByte = []

    # Converts each 8 bits to a byte and appends it to the bytearray
    while localUnicodeBits:
        currentByte = []
        for i in range(BYTE_SIZE):
            currentByte.append(localUnicodeBits.pop(0))
        byteStr = ''.join(currentByte)
        byteVal = int(byteStr, BASE2)
        byteMessage.append(byteVal)

    return bytes(byteMessage)

