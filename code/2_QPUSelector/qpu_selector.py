"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Servicio encargado de seleccionar un conjunto de máquinas de QPU compatibles
para la ejecución de los microservicios que conforman la aplicación híbrida (cuántico-clásica)
"""
from kafka import KafkaConsumer, KafkaProducer
from ..config.config import KAFKA_SERVER_URL, TOPIC_QPU, TOPIC_QPU_CANDIDATES
import json
import logging

"""
JSON SALIDA

app : {
        microservice_1: {
            qpu_machines : []
        }, 
        ...
        microservice_n {
            qpu_machines : []
        }
    }

"""

def select_qpu(qubits, shots):
    """
    RETURN FORMAT 
    selected_qpus = [
        machine_1 : {
        characteristic_1 : value,
        characteristic_2 : value,
        ...
        },
        machine_2 : {
        characteristic_1 : value,
        characteristic_2 : value,
        ...
        }
        ...
    ]
    
    """
    selected_qpus = []
    return selected_qpus

if __name__ == '__main__':
    consumer = KafkaConsumer(TOPIC_QPU, bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.loads(x).encode('utf-8')) # CREATING KAFKA CONSUMER
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    logging.basicConfig(filename='qpu-selector.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    app_qpu_machines = dict()
    for message in consumer:
        logging.debug("QPU-SELECTOR : MESSAGE RECIEVED")
        microservices = message.value

        for microservice_name, requirements in microservices.items():
            logging.debug("QPU-SELECTOR : PROCESSING MICROSERVICE" + microservice_name)
            app_qpu_machines[microservice_name] = select_qpu(requirements['qubits'], requirements['shots']) # Returns an Array<Dict> of the suitable CPUs machines from AWs

