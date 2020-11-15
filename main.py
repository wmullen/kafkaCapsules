import kafkaCapsule as kc

capsule = kc.KafkaCapsule("test1", 123)
capsule.createCapsule
testData = "Test Data"
testData = testData.encode("utf-8")
capsule.append(testData)
data = capsule.read()
print(data[0].decode("utf-8"))