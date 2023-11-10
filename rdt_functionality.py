import random
import numpy as np
from type_manipulation import *

BYTE_SIZE =         8
BASE2 =             2
BASE10 =            10
SEED =              1083430
FAIL =              True
SUCCESS =           False

def corruptPkt(msg: str, numCorrupts=0, error_prob=0, burst=0):
    # This function takes a message string of a packet which contains a header
    # and a payload, the number of bits of the payload that should be corrupted, 
    # the probability of corruption, and the length of the burst error if
    # the corruption should be a burst error instead of random bit errors. 
    # It separates the information and the 
    # payload, uses the corrupt() function to corrupt the payload and returns 
    # a new message string with the header and corrupted payload.

    if random.randint(0,100) < error_prob:
        [header, payload] = msg.split('\n', 1)
        if not burst:
            corruptPayload = corrupt(payload.encode('utf-8'), numCorrupts)
        else:
            corruptPayload = burstError(payload.encode('utf-8'), burst)
        corruptPkt = header + '\n' + str(corruptPayload).strip("b'")
        return corruptPkt
    else:
        return msg

def corrupt(msg: bytearray(), numCorrupts: int):
    # This function takes a message bytearray() and number of bits the user wants to corrupt.
    # It uses Python's "Random" module to randomly choose bits to flip,
    # and returns the corrupted bytearray().

    binMsg = bytes2Bin(msg)
    corruptedBinMsg = __corruptBits(binMsg, numCorrupts)
    corruptedBytesMsg = bin2Bytes(corruptedBinMsg)
    return corruptedBytesMsg

def burstError(msg: bytearray(), burstLength: int):
    # This function takes a bytearray() message and the 
    # desired length of the burst error as an integer. 
    # It uses Python's "Random" module to randomly choose an initial bit,
    # flips bits following the initial bit for the burstLength,
    # and returns the corrupted bytearray() message.

    binMsg = bytes2Bin(msg)
    burstErrorBinMsg = __burstErrorBits(binMsg, burstLength)
    burstErrorBytesMsg = bin2Bytes(burstErrorBinMsg)
    return burstErrorBytesMsg

def generateUDPChecksum(msg: bytearray()):
    # This function takes a bytearray() message generates a checksum
    # for it as a list of bit characters.

    binMsg = bytes2Bin(msg)
    checksumBits = __generateUDPChecksumBits(binMsg)
    return checksumBits

def verifyUDPChecksum(msg: bytearray(), checksum: list):
    # This function takes a bytearray() message and the checksum as a 
    # list of bit characters.
    # Returns 0 if the checksum is verified correctly.
    # Returns 1 otherwise.

    binMsg = bytes2Bin(msg)
    return __verifyUDPChecksumBits(binMsg, checksum)


def __verifyUDPChecksumBits(unicodeBits: list, checksum: list):
    # This function takes the unicode list of bit characters and the checksum as a 
    # list of bit characters.
    # Returns 0 if the checksum is verified correctly.
    # Returns 1 otherwise.

    localChecksum = checksum[:]
    verify = __generateUDPChecksumBits(unicodeBits + localChecksum)

    for bit in verify:
        if (bit == '1'):
            return 1
    return 0

def generate2DParityCheck(msg: bytearray()):
    # This function takes a bytearray() message,
    # forms it into an array and returns a 2D parity check 
    # as a list of bit integers.

    # Initialising 
    unicodeBits = bytes2Bin(msg)
    numBytes = len(unicodeBits) // BYTE_SIZE
    bytes2DArray = np.empty((numBytes, BYTE_SIZE))
    bitSum = 0
    parityList = []

    # Putting each byte into an array
    for byteIdx in range(numBytes):
        for i in range(BYTE_SIZE):
            bytes2DArray[byteIdx, i] = int(unicodeBits[byteIdx*BYTE_SIZE + i])

    # Generating even parity bit for each row and column.
    # Iterating through all rows

    for rowIdx in range(numBytes):
        bitSum = np.sum(bytes2DArray[rowIdx, :])
        if __isEven(bitSum):
            parityList.append(0)
        else:
            parityList.append(1)
            
    # Iterating through all columns
    for colIdx in range(BYTE_SIZE):
        bitSum = np.sum(bytes2DArray[:, colIdx])
        if __isEven(bitSum):
            parityList.append(0)
        else:
            parityList.append(1)

    return parityList

def verify2DParityCheck(msg: bytearray(), sndrParityBits: list):
    # Takes a bytearray() message and a parity list
    # of bit integers. Corrects up to 1 bit error, 
    # and verifies whether the data is corrupted or not.
    # Returns the corrected bytearray() message and false if the check succeeds,
    # an None and true if the payload is corrupt and cannot be corrected.

    # Note: 2D parity check can only detect up to 2 bit errors.

    # Initialising
    unicodeBits = bytes2Bin(msg)
    numRows = len(sndrParityBits) - BYTE_SIZE
    numCols = BYTE_SIZE
    recvParityBits = generate2DParityCheck(msg)
    rowErrorIdx = None
    colErrorIdx = None

    # Verifying row parity
    for rowIdx in range(numRows):
        if sndrParityBits[rowIdx] != recvParityBits[rowIdx]:
            if rowErrorIdx == None:
                rowErrorIdx = rowIdx
            else:
                return None, FAIL
            
    # Verifying column parity
    for colIdx in range(numCols):
        if sndrParityBits[numRows+colIdx] != recvParityBits[numRows+colIdx]:
            if colErrorIdx == None:
                colErrorIdx = colIdx
            else:
                return None, FAIL

    # Correcting errors
    if ((rowErrorIdx == None) and (colErrorIdx != None)) or ((rowErrorIdx != None) and (colErrorIdx == None)):
        return None, FAIL
    elif (rowErrorIdx != None) and (colErrorIdx != None):
        if unicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] == '1':
            unicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] = '0'
        else:
            unicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] = '1'

    return bin2Bytes(unicodeBits), SUCCESS

def __isEven(val: int):
    if (val % 2) == 0:
        return True
    else:
        return False

def __burstErrorBits(unicodeBits: list, burstLength: int):
    # This function takes a unicode list of bit characters and the 
    # desired length of the burst error as an integer. 
    # It uses Python's "Random" module to randomly choose an initial bit,
    # flips bits following the initial bit for the burstLength,
    # and returns the corrupted list of bit characters.

    corruptedUnicode = unicodeBits[:]

    # stops trying to corrupt bits that are out of range
    if burstLength > len(corruptedUnicode):
        initialCorrupt = 0

    else:
        initialCorrupt = random.randrange(0, len(corruptedUnicode)-burstLength)

    for i in range(initialCorrupt, min(initialCorrupt+burstLength, len(corruptedUnicode))):
        if corruptedUnicode[i] == '0':
            corruptedUnicode[i] = '1'
        else:
            corruptedUnicode[i] = '0'
    return corruptedUnicode

def __corruptBits(unicodeBits: list, numCorrupts: int):
    # This function takes a unicode list of bit characters and the number of bits the user
    # wants to corrupt. It uses Python's "Random" module to randomly choose bits to flip,
    # and returns the corrupted list of bit characters.

    corruptedUnicode = unicodeBits[:]
    corruptIdxs = random.sample(range(0, len(corruptedUnicode)), numCorrupts)
    for corruptIdx in corruptIdxs:
        if corruptedUnicode[corruptIdx] == '0':
            corruptedUnicode[corruptIdx] = '1'
        else:
            corruptedUnicode[corruptIdx] = '0'
    return corruptedUnicode

def __generateUDPChecksumBits(unicodeBits: list):
    # This function takes a unicode list of bit characters and generates a checksum
    # for as a list of bit characters.

    # Initialising 
    localUnicodeBits = unicodeBits[:]
    currentByte = ''
    nextByte = ''

    # Grabs each byte and mod2 sums it with the next one
    while localUnicodeBits:
        nextByte = ''
        for i in range(BYTE_SIZE):
            nextByte = nextByte + localUnicodeBits.pop(0)
        if currentByte:
            currentByte = (bin(int(currentByte, 2) + int(nextByte, 2)))[2:]
        else:
            currentByte = nextByte
        while len(currentByte) > BYTE_SIZE:     # Then there has been overflow!
            currentByte = currentByte[1:]
            currentByte = (bin(int(currentByte, 2) + 1))[2:]

    checksum = list(currentByte)
    # Pad with leading 0's
    while (len(checksum) < BYTE_SIZE):
        checksum.insert(0, '0')

    # One's complement
    for bitIdx in range(len(checksum)):
        if checksum[bitIdx] == '0':
            checksum[bitIdx] = '1'
        else:
            checksum[bitIdx] = '0'

    return checksum

def __generate2DParityCheckBits(unicodeBits: list):
    # This function takes a unicode list of bit characters,
    # forms it into an array and adds a row and column
    # for even parity bits.

    # Initialising 
    numBytes = len(unicodeBits) // BYTE_SIZE
    bytes2DArray = np.empty((numBytes+1, BYTE_SIZE+1))
    sum = 0

    # Putting each byte into an array
    for byteIdx in range(numBytes):
        for i in range(BYTE_SIZE):
            bytes2DArray[byteIdx, i] = int(unicodeBits[byteIdx*BYTE_SIZE + i])

    # Generating even parity bit for each row and column.

    # Iterating through all rows
    for rowIdx in range((np.shape(bytes2DArray))[0] - 1):
        sum = np.sum(bytes2DArray[rowIdx, 0:-1])
        if __isEven(sum):
            bytes2DArray[rowIdx, -1] = 0
        else:
            bytes2DArray[rowIdx, -1] = 1

    # Iterating through all columns
    for colIdx in range((np.shape(bytes2DArray)[1]) - 1):
        sum = np.sum(bytes2DArray[0:-1, colIdx])
        if __isEven(sum):
            bytes2DArray[-1, colIdx] = 0
        else:
            bytes2DArray[-1, colIdx] = 1

    # Bottom right index is unused and needs to be set to 0
    bytes2DArray[-1, -1] = 0

    return bytes2DArray