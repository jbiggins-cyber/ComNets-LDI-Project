
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

    # Initialising
    i = 0
    currentBytes = []
    currentChar = ''
    uniqueVal = 0
    messageStr = ""
    bitStr = ""

    # Creating byte arrays
    while message:

        currentBytes = []
        unicodePrefix = ''.join(message[0:6])
        if unicodePrefix[0] == '0':                     # Unicode is 1 byte
            while i < 8:
                currentBytes += message.pop(0)
                i += 1
            bitStr = ''.join(currentBytes)
            uniqueVal = int(bitStr, 2)
            currentChar = chr(uniqueVal)
        elif unicodePrefix[0:3] == "110":    # Unicode is 2 bytes
            while i < 16:
                currentBytes += message.pop(0)
                i += 1
            bitStr = ''.join(currentBytes)
            uniqueVal = int(bitStr, 2)
            currentChar = chr(uniqueVal)
        elif unicodePrefix[0:5] == "1110":   # Unicode is 3 bytes
            while i < 24:
                currentBytes += message.pop(0)
                i += 1
            bitStr = ''.join(currentBytes)
            uniqueVal = int(bitStr, 2)
            currentChar = chr(uniqueVal)
        elif unicodePrefix[0:6] == "11110":  # Unicode is 4 bytes
            while i < 32:
                currentBytes += message.pop(0)
                i += 1
            bitStr = ''.join(currentBytes)
            uniqueVal = int(bitStr, 2)
            currentChar = chr(uniqueVal)
        else:                                       # Unicode is not valid, replace with asterisk
            while (i < 8) and message:
                message.pop(0)
                i += 1
            currentChar = '*'
        i = 0

        messageStr += currentChar
        
    return messageStr

def bytes2Bin(payload: bytes):
    # This function converts the received payload from bytes into a unicode binary array.
    # We need this function to verify a checksum.

    raise NotImplementedError()

message = "This is a tϧst message string!"
print("Original message: {}".format(message))
unicodeMessage = str2Bin(message)
print("Binary: {}".format(''.join(unicodeMessage)))
decodedMessage = bin2Str(unicodeMessage)
print("Decoded message: {}".format(decodedMessage))