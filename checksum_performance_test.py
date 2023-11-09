from rdt_functionality import *

NUM_SAMPLES = 10**5
SAMPLE = "Hello, World! This is a test of the performance of checksum. :)"

def checksumErrorDetectRate(byteMsg: bytearray(), numErrors: int):
    # This function takes a bytearray() message and the number of desired bit errors
    # as an integer.
    # It creates a checksum, corrupts the message, then verifies it. 
    # Every message is corrupt and the function returns what percentage of the
    # corrupt messages are detected by UDP Checksum.

    numDetected = 0
    percentDetected = 0.0
    for i in range(NUM_SAMPLES):
        checksum = generateUDPChecksum(byteMsg)
        corruptByteMsg = corrupt(byteMsg, numErrors)
        if verifyUDPChecksum(corruptByteMsg, checksum) == 1:
            numDetected += 1
    percentDetected = numDetected / NUM_SAMPLES * 100
    return percentDetected

def checksumBurstErrorDetectRate(byteMsg: bytearray(), burstLength: int):
    # This function takes a bytearray() message and the desired length of a burst
    # error as an integer.
    # It creates a checksum, corrupts the message with one burst error, 
    # then verifies it 10^5 times. 
    # Every message is corrupt and the function returns what percentage of the
    # corrupt messages are detected by UDP Checksum.

    numDetected = 0
    percentDetected = 0.0
    for i in range(NUM_SAMPLES):
        checksum = generateUDPChecksum(byteMsg)
        corruptByteMsg = burstError(byteMsg, burstLength)
        if verifyUDPChecksum(corruptByteMsg, checksum) == 1:
            numDetected += 1
    percentDetected = numDetected / NUM_SAMPLES * 100
    return percentDetected

# Printing byte message
byteMsg = SAMPLE.encode('utf-8')
print("""Sample message: "{}" """.format(byteMsg))
print("# bits in sample message: {}".format(len(str2Bin(SAMPLE))))

# Print the percentage of errors detected for different numbers of bit errors
numErrors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16]
for i in numErrors:
    print("Num Errors: {}, \% Detectected: {}".format(i, checksumErrorDetectRate(byteMsg, i)))

# Print the percentage of errors detected for different length burst errors
burstLen = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
for i in burstLen:
    print("Num Errors: {}, \% Detectected: {}".format(i, checksumBurstErrorDetectRate(byteMsg, i)))