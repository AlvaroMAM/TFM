from kafka import KafkaConsumer
from ..topics.topics import TOPIC_WEB

consumer = KafkaConsumer(TOPIC_WEB)

for message in consumer:
    print(message)