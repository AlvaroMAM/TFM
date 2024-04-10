"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Servicio encargado de seleccionar un conjunto de máquinas de CPU compatibles
para la ejecución de los microservicios que conforman la aplicación híbrida (cuántico-clásica)
"""
from kafka import KafkaConsumer, KafkaProducer
from ..config.config import KAFKA_SERVER_URL, TOPIC_CPU, TOPIC_CPU_CANDIDATES
import json
import logging
"""
JSON SALIDA
app : {
        microservice_1: {
            cpu_machines : [],
        }, 
        ...
        microservice_n {
            cpu_machines : [],
        }
    }
"""

if __name__ == '__main__':
    consumer = KafkaConsumer(TOPIC_CPU, bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.loads(x).encode('utf-8')) # CREATING KAFKA CONSUMER
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    logging.basicConfig(filename='cpu-selector.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    app_cpu_machines = dict()
    for message in consumer:
        print(message)
