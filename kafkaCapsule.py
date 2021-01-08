from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from hashlib import sha256
from capsuleMetadata import CapsuleMetadata
from dataHeader import DataHeader
import pickle

class KafkaCapsule():
    def __init__(self, pubWriterKey, topic_name):
        self.gdpName = sha256(bytes(pubWriterKey + topic_name, encoding='utf-8')).hexdigest()
        self.dataTopic = self.gdpName + '_data'
        self.headerTopic = self.gdpName + '_header'
        self.pubWriterKey = pubWriterKey
        self.admin_client = KafkaAdminClient(
            bootstrap_servers='localhost:9092',
            client_id=pubWriterKey
        )
        self.topic_name = topic_name
        self.ready = False

    def createCapsule(self):
        # Create new topics
        if (self.pubWriterKey is None):
            print('Error, invalid pubwriter key')
            return

        try:
            topic_list = [NewTopic(name=self.dataTopic, num_partitions=1, replication_factor=1), 
                          NewTopic(name=self.headerTopic, num_partitions=1, replication_factor=1)]
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
        except:
            print('Topic already exists, use load instead')
            return

        # Append capsule metadata
        metadata = CapsuleMetadata(self.gdpName, self.pubWriterKey)
        value = pickle.dumps(metadata)
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        producer.send(self.dataTopic, value=value)
        producer.send(self.headerTopic, value=value)

        print('Topic created!')
        self.ready = True
        return self.getName()

    def loadCapsule(self, gdpName):
        # Pull basic information
        self.gdpName = gdpName
        self.dataTopic = gdpName + '_data'
        self.headerTopic = gdpName + '_header'
        
        # Pull metadata information
        metadataConsumer = KafkaConsumer(self.dataTopic, 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest', 
            max_poll_records=0)
        metadata = None
        for msg in metadataConsumer:
            metadata = pickle.loads(msg.value)
            metadataConsumer.close()
            break
        self.pubWriterKey = metadata.pubWriterKey

        self.ready = True
        print('Capusle loaded!')

    def append(self, data):
        # Ensure capsule has been created or loaded
        if not self.ready:
            print('Error, capsule not created or loaded')
            return

        # Append data
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        producer.send(self.dataTopic, value=data)

        # Generate headers
        headers = []
        consumer = KafkaConsumer(self.dataTopic, 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest', 
            consumer_timeout_ms=100)
        for message in consumer:
            headers.append(message.value)
        
        newHeader = None
        if len(headers) == 1:
            prevHash = sha256(headers[0]).digest()
            newHeader = DataHeader(0, self.getName, None, prevHash, sha256(data).digest())
        else:
            prevHash = sha256(headers[-1]).digest()
            doublePrevHash = sha256(headers[-2]).digest()
            newHeader = DataHeader(0, self.getName, doublePrevHash, prevHash, sha256(data).digest())

        producer.send(self.headerTopic, pickle.dumps(newHeader))
        print('Appended: ', data)

    def read(self, offset=0):
        # Ensure capsule has been created or loaded
        if not self.ready:
            print('Error, capsule not created or loaded')
            return

        # Read data
        # TODO: Verify hashes
        data = []
        consumer = KafkaConsumer(self.dataTopic, 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest', 
            consumer_timeout_ms=1000)
        # consumer.seek((0), offset)
        for message in consumer:
            data.append(message.value)
        return data
    
    def readLast(self):
        # TODO: All of this
        tp = TopicPartition(self.dataTopic, 0)
        consumer = KafkaConsumer(self.dataTopic, 
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest', 
        consumer_timeout_ms=1000)
        consumer.seek_to_end(tp)
        return consumer.poll(max_records=1)

    def subscribe(self):
        if self.getName() == 'heartbeats':
            consumer = KafkaConsumer('heartbeats', 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest')
            return consumer
        else:
            consumer = KafkaConsumer(self.getName() + '_data', 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest', 
            consumer_timeout_ms=1000)
    
    def getName(self):
        return self.gdpName