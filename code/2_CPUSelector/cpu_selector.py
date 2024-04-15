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
import os

"""
# JSON ENTRADA
{
file_name : {
    id : x,
    mode : y,
    requests: z,
    execution_time: h,
    ram: j,
    cpu: k
    }
}

# JSON SALIDA
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
def is_candidate(machine_information,ms_requests, ms_execution_time, ms_cpu, ms_ram):
    return machine_information['requests']>= ms_requests and machine_information['ram'] >= ms_execution_time and machine_information['cpu'] >= ms_cpu and machine_information['ram'] >= ms_ram
def select_cpu (requests, execution_time, cpu, ram):
    """
    # Leer archivo con características de las máquinas
    # Iterar por cada máquina, en cada iteración comprobar características si es compatible/candidata
    # Si lo es, añadir diccionario a lista
    RETURN FORMAT 
    selected_cpus = [
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
    selected_cpus = []
    cloud_providers_path = "./cloud-providers"
    cloud_providers_list = os.listdir(cloud_providers_path)
    for cloud_provider in cloud_providers_list:
        cloud_provider_file = os.path.join(cloud_providers_path+"/"+cloud_provider)
        if os.path.isfile(cloud_provider_file):
            cpu_machines = None
            with open(cloud_provider_file, 'r') as f:
                logging.debug("CPU-SELECTOR : CPU MACHINES READING")
                cpu_machines = json.load(f)
            for cpu_machine, data in cpu_machines.items():
                logging.debug("CPU-SELECTOR : CPU MACHINE" + cpu_machine + "PROCESSING")
                if is_candidate(data, requests, execution_time, cpu, ram):
                    selected_cpus.append((cpu_machine,data))
                    logging.debug("CPU-SELECTOR : CPU MACHINE" + cpu_machine + "IS CANDIDATE")
            continue
    return selected_cpus

if __name__ == '__main__':
    consumer = KafkaConsumer(TOPIC_CPU, bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.loads(x).encode('utf-8')) # CREATING KAFKA CONSUMER
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    logging.basicConfig(filename='cpu-selector.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    app_cpu_machines = dict()
    for message in consumer:
        print("CPU RECIEVED")
        """
        logging.debug("CPU-SELECTOR : MESSAGE RECIEVED")
        microservices = message.value

        for microservice_name, requirements in microservices.items():
            logging.debug("CPU-SELECTOR : PROCESSING MICROSERVICE:" + microservice_name)
            app_cpu_machines[microservice_name] = select_cpu(requirements['requests'], requirements['execution_time'], requirements['cpu'], requirements['ram']) # Returns an Array<Dict> of the suitable CPUs machines from AWS
            logging.debug("CPU-SELECTOR : MICROSERVICE PROCESSED:" + microservice_name)
        """