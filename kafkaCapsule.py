from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer

class KafkaCapsule():
    def __init__(self, topic_name=None, pubWriterKey=None):
        self.topic_name = topic_name
        self.gdpName = pubWriterKey
        self.pubWriterKey = pubWriterKey
        self.admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:9092",
            client_id=pubWriterKey
        )
        self.producer = None
        self.consumer = None

    def createCapsule(self):
        # Create new topic
        if (self.topic_name is None or self.pubWriterKey is None):
            print('Error, invalid pubwriter key and topic_name')
            return

        try:
            topic_list = [NewTopic(name=self.topic_name, num_partitions=1, replication_factor=1)]
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
        except:
            print("topic exists")

        # Append capsule metadata
        metadata = [self.pubWriterKey]
        KafkaProducer(bootstrap_servers=['localhost:9092']).send(self.topic_name, value=bytes(metadata))

    def loadCapsule(self, topic_name):
        # Pull basic information
        self.topic_name = topic_name
        
        # Pull metadata information
        metadataConsumer = KafkaConsumer(self.topic_name, 
            bootstrap_servers=["localhost:9092"],
            auto_offset_reset='earliest', 
            max_poll_records=0)
        metadata = None
        for msg in metadataConsumer:
            metadata = list(msg.value)
            metadataConsumer.close()
            break
        self.pubWriterKey = metadata[0]

        # Create produce and consumer
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        self.consumer = KafkaConsumer(self.topic_name, 
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset='earliest')

    def append(self, data):
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        producer.send(self.topic_name, value=data)
        print("Appended: ", data)

    def read(self, offset=0):
        data = []
        consumer = KafkaConsumer(self.topic_name, 
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset='earliest', 
        consumer_timeout_ms=1000)
        # consumer.seek((0), offset) BROKEN, partition must be a TopicPartition namedtuple
        for message in consumer:
            data.append(message.value)
        return data
    
    def readLast(self):
        self.consumer.seek_to_end()
        return self.consumer.poll()

    def subscribe(self):
        return