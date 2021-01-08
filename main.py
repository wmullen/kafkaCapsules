import kafkaCapsule as kc

# Check for heartbeat 

capsule = kc.KafkaCapsule('1234567', "test6")
capsuleName = capsule.createCapsule()
print('Capsule Name: ')
print(capsuleName)
testData = "Test Data"
testData = testData.encode("utf-8")
capsule.append(testData)
data = capsule.read()
print('Metadata: ' + data[0].decode("utf-8"))
print('Data: ' + data[1].decode("utf-8"))
