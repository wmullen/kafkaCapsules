from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
from hashlib import sha256

class KafkaCapsule():
    def __init__(self, pubWriterKey, topic_name=None):
        self.gdpName = sha256(bytes(pubWriterKey, encoding='utf-8')).hexdigest()
        self.dataTopic = self.gdpName + '_data'
        self.hashTopic = self.gdpName + '_hash'
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
                          NewTopic(name=self.hashTopic, num_partitions=1, replication_factor=1)]
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
        except:
            print('Topic already exists, use load instead')
            return

        # Append capsule metadata
        metadata = self.pubWriterKey
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        value = bytes(metadata, encoding='utf-8')
        producer.send(self.dataTopic, value=value)
        producer.send(self.hashTopic, value=value)

        print('Topic created!')
        self.ready = True
        return self.getName()

    def loadCapsule(self, gdpName):
        # Pull basic information
        self.gdpName = gdpName
        self.dataTopic = gdpName + '_data'
        self.hashTopic = gdpName + '_hash'
        
        # Pull metadata information
        metadataConsumer = KafkaConsumer(self.dataTopic, 
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest', 
            max_poll_records=0)
        metadata = None
        for msg in metadataConsumer:
            metadata = list(msg.value)
            metadataConsumer.close()
            break
        self.pubWriterKey = metadata[0]

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
        producer.send(self.hashTopic, value=sha256(data).digest())
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
        # consumer.seek((0), offset) BROKEN, partition must be a TopicPartition namedtuple
        for message in consumer:
            data.append(message.value)
        return data
    
    def readLast(self):
        # TODO
        return

    def subscribe(self):
        # TODO
        return
    
    def getName(self):
        return self.gdpName