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
from config.config import KAFKA_SERVER_URL, TOPIC_QPU, TOPIC_QPU_CANDIDATES
import json
import logging
import os

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

def is_candidate(machine_information, ms_qubits, ms_shots): 
    return machine_information['qubits']>= ms_qubits and \
    machine_information['shots_range']['minimum'] <= ms_shots and \
    machine_information['shots_range']['maximum'] >= ms_shots

def estimator(machine_information, ms_shots):
    return float(machine_information['device_cost']['price']) * ms_shots

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
    cloud_providers_path = "./cloud-providers"
    cloud_providers_list = os.listdir(cloud_providers_path)
    for cloud_provider in cloud_providers_list:
        cloud_provider_file = os.path.join(cloud_providers_path+"/"+cloud_provider)
        if os.path.isfile(cloud_provider_file):
            qpu_machines = None
            with open(cloud_provider_file, 'r') as f:
                logging.debug("QPU-SELECTOR : QUANTUM MACHINES READING")
                qpu_machines = json.load(f)
            for qpu_machine, machine_information in qpu_machines.items():
                logging.debug("QPU-SELECTOR : QUANTUM MACHINE" + qpu_machine + "PROCESSING")
                if is_candidate(machine_information, qubits, shots):
                    #ms_cost = estimator(data, shots)
                    qpu_machine_estimation = dict()
                    qpu_machine_estimation['qpu_prize'] = machine_information['device_cost']['price'] # Price per Shot
                    selected_qpus.append((qpu_machine,qpu_machine_estimation))
                    logging.debug("QPU-SELECTOR : QUANTUM MACHINE" + qpu_machine + "IS CANDIDATE")
    return selected_qpus

if __name__ == '__main__':
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    consumer = KafkaConsumer(TOPIC_QPU, bootstrap_servers=[KAFKA_SERVER_URL]) # CREATING KAFKA CONSUMER
    logging.basicConfig(filename='qpu-selector.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    app_qpu_machines = dict()
    print("QPU SELECTOR STARTED")
    for message in consumer:
        print("MICROSERVICES RECIEVED")
        logging.debug("QPU-SELECTOR : MESSAGE RECIEVED")
        microservices = json.loads(message.value.decode('utf-8'))
        for microservice_name, requirements in microservices.items():
            logging.debug("QPU-SELECTOR : PROCESSING MICROSERVICE: " + microservice_name)
            app_qpu_machines[microservice_name] = {} # initializing json of microservice
            app_qpu_machines[microservice_name]['selected_qpu'] = select_qpu(requirements['qubits'], requirements['shots']) # Returns an Array<Dict> of the suitable CPUs machines from AWs
            app_qpu_machines[microservice_name]['shots'] = requirements['shots']
            logging.debug("QPU-SELECTOR : MICROSERVICE PROCESSED" + microservice_name)
        print(app_qpu_machines)