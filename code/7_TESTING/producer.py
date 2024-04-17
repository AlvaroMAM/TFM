from kafka import KafkaProducer
from time import sleep
producer = KafkaProducer(bootstrap_servers='192.168.18.12:9092')
print("CREATED PRODUCER")
for _ in range(100):
    message = b'message_' + str(_).encode()
    producer.send('information', message)
    print("Message sent:", message)
    sleep(1)