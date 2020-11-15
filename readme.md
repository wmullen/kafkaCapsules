# Warning, this code is heavily in development and will change on a whim.  Things will break.

This code is an initial attempt at creating a cohesive way for representing a basic
Data Capsule in Kafka using python 3.  It is heavily inspired by Nitesh's quickstart files
and Eric Chen's hackathon starter code.  

Do not forget to run start-kafka.sh!

The basic path is as follows.  Upon creating the object, you either pass in 
basic information as such as the pubWriterKey, or leave that all blank.  If passed
in, I assume the user will then call create on that information to create a new 
data capsule.  If it is not, then I assume the user will load a data capsule to 
populate those fields.  topic_name will eventually be replaced by gdpName, but is 
retained for debugging purposes.

Check main.py for a simple example.  

**Author:** William Mullen
