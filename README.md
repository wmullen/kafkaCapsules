# Warning, this code is heavily in development and will change on a whim.  Things will break.

# Introduction
This code is an initial attempt at creating a cohesive way for representing a basic
Data Capsule in Kafka using python 3.  It is inspired by Nitesh's quickstart files
and Eric Chen's hackathon starter code.  



The basic usage is as follows.  Upon creating the object, the user passes in a public writer (or signature) key.  If this is a new capsule, then the user calls `createCapsule`.  If this public writer key is already being used, then the user calls `loadCapsule` to populate the object with the capsule's information.  This will later be changed to support multiple capsules per key.  

Check main.py for a simple example.  

**Author:** William Mullen

# Using the Capsules
## Setup
1. Install [Docker](https://docs.docker.com/get-docker/).
2. If not on Mac or Windows, install [Docker Compose](https://docs.docker.com/compose/install/).
3. Install [Python 3](https://www.python.org/downloads/).
4. Run `pip install kafka-python`.

## Running Code
1. Run `start-kafka.sh`.
2. Run your python file.

## Teardown

In the event something goes horribly wrong with Kafka or you would like to reset your topics, following this section, deleting the containers, and then running `start-kafka.sh` will pull a fresh copy of the Kafka containers.  The steps detailed here are mainly for users running on Linux, as Docker Desktop will handle these operations through the Dashboard.  The process is generally the same, find the containers, stop them, and then delete if desired.

1. Run `docker ps` and find the names associated with the `confluentinc/cp-kafka` and `confluent/zookeeper containers`.  If you are using Docker Desktop, simply navigate to your Dashboard.
2. Run `docker stop [container name]` using the names you found in step 1. 
3. If desired, run `docker rm [container name]` on both containers.  WARNING: This will wipe any capsules you have created.  Only do this step if you want a fresh copy of Kafka or are done with KafkaCapsules.  

# KafkaCapsule Documentation
A KafkaCapsule emulates a Data Capsule as originally described using two Kafka topics.

As originally described, a Data Capsule consists of a long chain of records that form a skewed tree.  While one topic would suffice, I instead propose a two topic architecture as follows:

![KafkaCapsule structure](/images/kafkaCapsules.png)

The first record in both topics is the metadata for the capsule.  The data is mirrored and immutable.  Next, the data topic, labelled GDPName_Data in the above diagram, holds the actual data that has been appended.  The second topic, labelled GDPName_Header, contains the header for the corresponding data.  Because there is no way to read individual records in a Kafka topic, this structure makes it possible to do proof checking without having to download all the data.  Instead, just accessing the header topic would be sufficient to verify all the signatures and hashes are correct.  

An additional topic would also exist for maintaining heartbeats.  This would be a compacted topic, with length equal to the number of KafkaCapsules, that is updated with new heartbeats whenever a new append is made.  Since the topic is compacted, when a new record representing a capsule update is added to this topic, the older heartbeat for the same capsule is automatically discarded.  Thus, this system correctly emulates the same heartbeat behavior seen in well-behaving log servers.  


## KafkaCapsule Attributes
A KafkaCapsule has the following attributes:

1. `gdpName`
    * A 256 bit name that identifies this KafkaCapsule.  Currently a sha256 hash of the `pubWriterKey`. 
2. `dataTopic`
    * An internally used name for the data Kafka topic (see image above).  Generated by adding `_data` to the end of the `gdpName`.  
3. `headerTopic`
    * An internally used name for the header Kafka topic (see image above).  Generated by adding `_header_` to the end of the `gdpName`.  
4. `pubWriterKey`
    * A stored version of the public signature key of the owner of this capsule.
5. `self.admin_client`
    * An internal client used to create the two topics.
6. `topic_name`
    * Internal human readable name retained for debugging purposes.  This is not stored in Kafka.
7. `self.ready`
    * This flag is initialized to False but is set to True upon successful call to `createCapsule` or `loadCapsule`.  Indicates whether a capsule is ready to be read from or written to.  There is almost certainly a better way to do this check.    

## KafkaCapsule Functions
### `createCapsule(self)`
Creates a new capusle based on a hash of the object's `pubWriterkey` and `topic_name`.  First checks to see if a capsule already exists with this name.  If not, then two new Kafka topics are spawned, one for the capsule's data and another for its headers.  Once successfully finished, sets the `ready` flag to true and prints a notification.  Returns the capsule's `gdpName` upon success.

### `loadCapsule(self, gdpName)`
Loads the information for a capsule with name `gdpName` into the object.  This populates the `gdpName`, `dataTopic`, `hashTopic`, and `pubWriterKey` fields.  Once successfully finished, sets the `ready` flag to true and prints a notification.  This function does not return anything.

### `append(self, data)`
Appends `data` to the end of the capsule represented by this object.  Under the hood, this function appends the data to the `dataTopic` and the data's header to the `headerTopic`.  Assumes data is already a bytestring. This function prints when the append is complete and does not return anything.

### `read(self, offset=0)`
Reads the data stored in the capsule represented by this object and returns the byte strings in a list.  The offset is not yet implemented but will eventually allow for reading starting at a certain record.  Currently does not verify hashes.

### `readLast(self)`
Not yet implemented.  Will eventually return only the more recent record in the capsule.  

### `subscribe(self)`
This function returns a consumer subscribed to the `gdpName` attached to this object.  Does not require a call to `load`.    

### `getName(self)`
Returns the `gdpName` stored in this object.  

# Next Steps
Project status has moved! See it [here](https://docs.google.com/spreadsheets/d/1QuNKCmNz51L1ffJxc4ATpewFE0DxSTTQ02T6d6clJ9s/edit?usp=sharing)
