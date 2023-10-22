from rdt_functionality import *

print()
message = "This is a test message string!"
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

print()
corruptedBits = __corruptBits(unicodeMessage, 1)
corruptedMessage = bin2Bytes(corruptedBits)
print("Original message bytes:           {}".format(byteArr))
print("Corrupted original message bytes: {}".format(corruptedMessage))

print()
checksum = __generateUDPChecksumBits(unicodeMessage)
print("Checksum of original message: {}".format(checksum))
print("Checksum verification of original message: {}".format(__verifyUDPChecksumBits(unicodeMessage, checksum)))
print("Checksum verification of corrupted message: {}".format(__verifyUDPChecksumBits(corruptedBits, checksum)))

print()
bytesArray = __generate2DParityCheck(unicodeMessage)
print("Bytes array: {}".format(bytesArray))
sndrParity2DList = generate2DParityCheck(unicodeMessage)
[correctedBits, success] = verify2DParityCheck(corruptedBits, sndrParity2DList)
if success == SUCCESS: 
    correctedMessage = bin2Str(correctedBits)
    print("Corrected message: {}".format(correctedMessage))

print()
someBits = ['0', '1', '1', '0', '1', '0', '0', '1']
print("Original message: {}".format(byteArr))
burstedBytes = burstError(byteArr, 16)
print("Burst error msg : {}".format(burstedBytes))

print()
print("Corrupted bytes: {}".format(corrupt(byteArr, 2)))