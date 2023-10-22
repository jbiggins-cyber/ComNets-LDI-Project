from rdt_functionality import *

NUM_SAMPLES = 10**5
SAMPLE = "Hello, World! This is a test of the performance of checksum. :)"

def checksumErrorDetectRate(byteMsg: bytearray(), numErrors: int):
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
    numDetected = 0
    percentDetected = 0.0
    for i in range(NUM_SAMPLES):
        checksum = generateUDPChecksum(byteMsg)
        corruptByteMsg = burstError(byteMsg, burstLength)
        if verifyUDPChecksum(corruptByteMsg, checksum) == 1:
            numDetected += 1
    percentDetected = numDetected / NUM_SAMPLES * 100
    return percentDetected

byteMsg = SAMPLE.encode('utf-8')

print("""Sample message: "{}" """.format(byteMsg))
print("# bits in sample message: {}".format(len(str2Bin(SAMPLE))))

numErrors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16]

for i in numErrors:
    print("Num Errors: {}, \% Detectected: {}".format(i, checksumErrorDetectRate(byteMsg, i)))

burstLen = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

for i in burstLen:
    print("Num Errors: {}, \% Detectected: {}".format(i, checksumBurstErrorDetectRate(byteMsg, i)))