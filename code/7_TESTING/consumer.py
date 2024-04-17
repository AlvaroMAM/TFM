from kafka import KafkaConsumer
consumer = KafkaConsumer('information',bootstrap_servers='192.168.18.12:9092')
print("CONSUMER CREATED")
for msg in consumer:
    print("Message received:", msg.value.decode('utf-8'))