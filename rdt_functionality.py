import random
import numpy as np
from type_manipulation import *

BYTE_SIZE =         8
BASE2 =             2
BASE10 =            10
SEED =              1083430
FAIL =              True
SUCCESS =           False

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

def verifyUDPChecksum(unicodeBits: list, checksum: list):
    # This function takes the unicode list of bit characters and the checksum as a 
    # list of bit characters.
    # Returns 0 if the checksum is verified correctly.
    # Returns 1 otherwise

    localChecksum = checksum[:]
    verify = __generateUDPChecksumBits(unicodeBits + checksum)

    for bit in verify:
        if (bit == '1'):
            return 1
    return 0

def generate2DParityCheck(unicodeBits: list):
    # This function takes a unicode list of bit characters,
    # forms it into an array and returns a 2D parity check 
    # as a list of bit integers.

        # Initialising 
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
    for rowIdx in range((np.shape(bytes2DArray))[0]):
        bitSum = np.sum(bytes2DArray[rowIdx, :])
        if __isEven(bitSum):
            parityList.append(0)
        else:
            parityList.append(1)
    # Iterating through all columns
    for colIdx in range((np.shape(bytes2DArray)[1])):
        bitSum = np.sum(bytes2DArray[:, colIdx])
        if __isEven(bitSum):
            parityList.append(0)
        else:
            parityList.append(1)
    return parityList

def verify2DParityCheck(unicodeBits: list, sndrParityBits: list):
    # Takes a unicode list of bit characters and a parity list
    # of bit integers. Corrects up to 1 bit error, 
    # and verifies whether the data is corrupted or not.
    # Returns the corrected unicode bits and false if the check succeeds,
    # an empty list and true if the payload is corrupt and cannot be corrected.

    # Note: 2D parity check can only detect up to 2 bit errors.

    # Initialising
    localUnicodeBits = unicodeBits[:]
    numRows = len(sndrParityBits) - BYTE_SIZE
    numCols = BYTE_SIZE
    recvParityBits = generate2DParityCheck(localUnicodeBits)
    rowErrorIdx = None
    colErrorIdx = None

    # Verifying row parity
    for rowIdx in range(numRows):
        if sndrParityBits[rowIdx] != recvParityBits[rowIdx]:
            if rowErrorIdx == None:
                rowErrorIdx = rowIdx
            else:
                print("More than 1 bit error detected, 2D parity check failed!\n")
                return [], FAIL
            
    # Verifying column parity
    for colIdx in range(numCols):
        if sndrParityBits[numRows+colIdx] != recvParityBits[numRows+colIdx]:
            if colErrorIdx == None:
                colErrorIdx = colIdx
            else:
                print("More than 1 bit error detected, 2D parity check failed!\n") 
                return [], FAIL

    # Correcting errors
    if ((rowErrorIdx == None) and (colErrorIdx != None)) \
        or ((rowErrorIdx != None) and (colErrorIdx == None)):
        print("More than 1 bit error detected, 2D parity check failed!\n") 
        return [], FAIL
    elif (rowErrorIdx != None) and (colErrorIdx != None):
        if localUnicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] == '1':
            localUnicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] = '0'
        else:
            localUnicodeBits[rowErrorIdx*BYTE_SIZE + colErrorIdx] = '1'

    # Checking if there were hidden bit errors
    recvParityBits = generate2DParityCheck(localUnicodeBits)

    # Verifying row parity
    for rowIdx in range(numRows):
        if sndrParityBits[rowIdx] != recvParityBits[rowIdx]:
            if rowErrorIdx == None:
                rowErrorIdx = rowIdx
            else:
                print("More than 1 bit error detected, 2D parity check failed!\n")
                return [], FAIL
            
    # Verifying column parity
    for colIdx in range(numCols):
        if sndrParityBits[numRows+colIdx] != recvParityBits[numRows+colIdx]:
            if colErrorIdx == None:
                colErrorIdx = colIdx
            else:
                print("More than 1 bit error detected, 2D parity check failed!\n") 
                return [], FAIL

    return [localUnicodeBits, SUCCESS]

def __isEven(val: int):
    if val % 2 == 0:
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
    initialCorrupt = random.randrange(0, len(corruptedUnicode)-burstLength)
    for i in range(initialCorrupt, initialCorrupt+burstLength):
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

    # Grabs each byte and checksums it with the next one
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

def __generate2DParityCheck(unicodeBits: list):
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