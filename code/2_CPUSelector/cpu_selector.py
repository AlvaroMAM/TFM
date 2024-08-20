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
from config.config import KAFKA_SERVER_URL, TOPIC_CPU, TOPIC_CPU_CANDIDATES, TOPIC_BEHAVIOURAL, TOPIC_WEB
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
# Number of request = Request por minute
# Maximun request size = Bytes
# Hacer transformación ms_cpu --> GHz
def is_candidate(machine_information, ms_logical_performance_cpu, ms_ram, ms_bandwidth):
    return (float(machine_information['virtual_cpu'])*float(machine_information['cores_cpu'])*float(machine_information['ghz_cpu']))>= ms_logical_performance_cpu \
            and float(machine_information['ram']) >= float(ms_ram) \
            and int(machine_information['bandwidth']) >= ms_bandwidth

"""
NOT NECESSARY IS CALCULATED IN HAIQ
# Availability = number of hours
def estimator(machine_information, ms_logical_performance_cpu, ms_ram, ms_bandwidth):
    # Consideramos que las tres variables afectan por igual al cálculo del tiempo de ejecución
    estimated_execution_time_factor = (float(ms_logical_performance_cpu)/(float(machine_information['virtual_cpu'])*float(machine_information['cores_cpu'])*float(machine_information['ghz_cpu'])) \
                                + float(ms_ram)/float(machine_information['ram']) \
                                + int(ms_bandwidth)/int(machine_information['bandwidth']))/3 
    
    return estimated_execution_time_factor
"""

def select_cpu (logical_performance_cpu, ram, bandwidth):
    """
    # Leer archivo con características de las máquinas
    # Iterar por cada máquina, en cada iteración comprobar características si es compatible/candidata
    # Si lo es, calcular estimación de costo y rendimiento y añadir diccionario a lista
    RETURN FORMAT 
    selected_cpus = [
        machine_1 : {
        characteristic_1 : value,
        characteristic_2 : value,
        execution_time: value,
        cost : value
        ...
        },
        machine_2 : {
        characteristic_1 : value,
        characteristic_2 : value,
        execution_time: value,
        cost : value
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
            for cpu_machine, machine_information in cpu_machines.items():
                logging.debug("CPU-SELECTOR : CPU MACHINE" + cpu_machine + "PROCESSING")
                if is_candidate(machine_information, logical_performance_cpu, ram, bandwidth):
                    #ms_execution_time_factor, ms_cost =  estimator(machine_information, logical_performance_cpu, ram, bandwidth)
                    cpu_machine_estimation = dict()
                    cpu_machine_estimation['cpu_logical_performance_factor'] = (float(machine_information['virtual_cpu'])*float(machine_information['cores_cpu'])*float(machine_information['ghz_cpu']))
                    cpu_machine_estimation['cpu_ram'] = float(machine_information['ram'])
                    cpu_machine_estimation['cpu_bandwidth'] = int(machine_information['bandwidth'])
                    cpu_machine_estimation['cpu_cost_factor'] = machine_information['prize']
                    selected_cpus.append((cpu_machine.replace(".","_"),cpu_machine_estimation))
                    logging.debug("CPU-SELECTOR : CPU MACHINE" + cpu_machine + "IS CANDIDATE")
            continue
    return selected_cpus

if __name__ == '__main__':
    consumer = KafkaConsumer(TOPIC_CPU, bootstrap_servers=[KAFKA_SERVER_URL]) # CREATING KAFKA CONSUMER
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    logging.basicConfig(filename='cpu-selector.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    app_cpu_machines = dict()
    print("CPU SELECTOR STARTED")
    producer.send(TOPIC_WEB, "CPU_SELECTOR")
    producer.flush()
    for message in consumer:
        print("MICROSERVICES RECIEVED")
        logging.debug("CPU-SELECTOR : MESSAGE RECIEVED")
        microservices = json.loads(message.value.decode('utf-8'))
        print("CLASSICAL MICROSERVICES READED CORRECTLY")
        for microservice_name, requirements in microservices.items():
            logging.debug("CPU-SELECTOR : PROCESSING MICROSERVICE --> " + microservice_name)
            # Transformation of cpu variable and calculation of bandwidth
            logical_performance_ms = requirements['cpu'] / 1_000_000_000 # From Cycles per second to GHz * 1 Core * 1 Virtual CPUs
            bandwidth_ms = (requirements['number_requests'] * 60 * requirements['maximum_request_size'] * 8 ) / 1_000_000 # From request per minute and max size of request to Mbps
            app_cpu_machines[microservice_name] = {} # initializing json of microservice
            app_cpu_machines[microservice_name]['ms_logical_performance_factor'] = logical_performance_ms
            app_cpu_machines[microservice_name]['ms_ram'] = requirements['ram']
            app_cpu_machines[microservice_name]['ms_bandwidth'] = bandwidth_ms
            app_cpu_machines[microservice_name]['ms_execution_time'] = requirements['execution_time']
            app_cpu_machines[microservice_name]['ms_availability'] = requirements['availability']
            app_cpu_machines[microservice_name]['ms_instances'] = requirements['instances']
            app_cpu_machines[microservice_name]['selected_cpus'] = select_cpu(logical_performance_ms, requirements['ram'], bandwidth_ms) # Returns an Array<Dict> of the suitable CPUs machines from AWS
            logging.debug("CPU-SELECTOR : MICROSERVICE PROCESSED --> " + microservice_name)
        print("CPU SELECTOR RESULT: ")
        print(app_cpu_machines)
        producer.send(TOPIC_CPU_CANDIDATES, app_cpu_machines)
        producer.flush()
        