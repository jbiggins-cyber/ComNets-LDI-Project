from rdt_functionality import *

NUM_SAMPLES = 10**5
SAMPLE = "This is a test of the performance of an error correcting code. :)"

def parityCheck2DDetectRate(byteMsg: bytearray(), numErrors: int):
    # This function takes a bytearray() message and the number of desired bit errors
    # as an integer.
    # It generates a 2D parity check, corrupts the message, then verifies it. 
    # Every message is corrupt and the function returns what percentage of the
    # corrupt messages are detected by 2D Parity Check and what percentage of them are
    # able to be corrected.

    numDetected = 0
    numCorrected = 0
    percentDetected = 0.0
    percentCorrected = 0.0
    for i in range(NUM_SAMPLES):
        parityCheck = generate2DParityCheck(byteMsg)
        corruptByteMsg = corrupt(byteMsg, numErrors)
        correctedByteMsg, verification = verify2DParityCheck(corruptByteMsg, parityCheck)
        if verification == FAIL:
            numDetected += 1
        elif correctedByteMsg == byteMsg:
            numDetected += 1
            numCorrected += 1
    percentDetected = numDetected / NUM_SAMPLES * 100
    percentCorrected = numCorrected / NUM_SAMPLES * 100
    return percentDetected, percentCorrected

def parityCheck2DBurstDetectRate(byteMsg: bytearray(), burstLength: int):
    # This function takes a bytearray() message and the length of a desired burst error.
    # It generates a 2D parity check, corrupts the message, then verifies it. 
    # Every message is corrupt and the function returns what percentage of the
    # corrupt messages are detected by 2D Parity Check and what percentage of them are
    # able to be corrected.

    numDetected = 0
    numCorrected = 0
    percentDetected = 0.0
    percentCorrected = 0.0
    for i in range(NUM_SAMPLES):
        parityCheck = generate2DParityCheck(byteMsg)
        corruptByteMsg = burstError(byteMsg, burstLength)
        correctedByteMsg, verification = verify2DParityCheck(corruptByteMsg, parityCheck)
        if verification == FAIL:
            numDetected += 1
        elif correctedByteMsg == byteMsg:
            numDetected += 1
            numCorrected += 1
    percentDetected = numDetected / NUM_SAMPLES * 100
    percentCorrected = numCorrected / NUM_SAMPLES * 100
    return percentDetected, percentCorrected

# Printing byte message
byteMsg = SAMPLE.encode('utf-8')
print("""Sample message: "{}" """.format(byteMsg))
print("# bits in sample message: {}".format(len(str2Bin(SAMPLE))))

# # Print the percentage of errors detected and of errors corrected for different numbers of bit errors
# numErrors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16]
# for i in numErrors:
#     percentDetected, percentCorrected = parityCheck2DDetectRate(byteMsg, i)
#     print("Num Errors: {}, Detected: {}%, Corrected: {}%".format(i, percentDetected, percentCorrected))
    
# Print the percentage of errors detected and corrected for different length burst errors
burstLen = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
for i in burstLen:
    percentDetected, percentCorrected = parityCheck2DBurstDetectRate(byteMsg, i)
    print("Burst Error Length: {}, Detected: {}%, Corrected: {}%".format(i, percentDetected, percentCorrected))