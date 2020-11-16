import kafkaCapsule as kc

capsule = kc.KafkaCapsule('12345', "test")
capsuleName = capsule.createCapsule()
testData = "Test Data"
testData = testData.encode("utf-8")
capsule.append(testData)
data = capsule.read()
print('Metadata: ' + data[0].decode("utf-8"))
print('Data: ' + data[1].decode("utf-8"))