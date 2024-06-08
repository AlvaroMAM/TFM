from kafka import KafkaConsumer
from config.config import KAFKA_SERVER_URL, TOPIC_QPU_CANDIDATES, TOPIC_CPU_CANDIDATES, TOPIC_BEHAVIOURAL
import json
import logging
import os

behavioural = None
cpu_candidates = None
qpu_candidates = None

def processing_topics():
    global behavioural, cpu_candidates, qpu_candidates
    # Procesar mensajes de los topics
    logging.debug("FILE-GENERATOR : WAITING FOR MESSAGES")
    for message in consumer:
        logging.debug("FILE-GENERATOR : MESSAGE RECIEVED")
        topic = message.topic
        if topic == TOPIC_BEHAVIOURAL:
            # Procesando Behavioural File
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC BEHAVIOURAL")
            file_message = message.value
            with open('received_file', 'w') as f:
                f.write(file_message)
            print(f"Procesado mensaje de archivo desde topic3 y guardado como received_file")
        elif topic == TOPIC_CPU_CANDIDATES:
            # Procesando CPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC CPU CANDIDATES")
            json1 = message.value
            print(f"Procesado mensaje JSON 1 desde topic1: {json1}")
        elif topic == TOPIC_QPU_CANDIDATES:
            # Procesando QPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC QPU CANDIDATES")
            json2 = message.value
            print(f"Procesado mensaje JSON 2 desde topic2: {json2}")
        if behavioural != None and cpu_candidates != None and qpu_candidates!=None:
            # Una vez leidas las 3, me salgo
            break


def classical_generator_string(candidates):
    services = ""
    machines = ""
    processed_machines = []
    logging.debug("FILE-GENERATOR : CLASSICAL GENERATOR STRING")
    for service_name, attributes in candidates.items():
        service_instance = "one "+service_name+" extends "+service_name.capitalize()+" {}\n"
        logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE CREATED")
        service_formulas = "</"
        if attributes["ms_logical_performance_factor"]:
            service_formulas="\nformula ms_logical_performance_factor = "+str(attributes["ms_logical_performance_factor"])+";"
        if attributes["ms_ram"]:
            service_formulas="\nformula ms_ram = "+str(attributes["ms_ram"])+";"
        if attributes["ms_bandwidth"]:
            service_formulas="\nformula ms_bandwidth = "+str(attributes["ms_bandwidth"])+";"
        if attributes["ms_execution_time"]:
            service_formulas="\nformula ms_execution_time = "+str(attributes["ms_execution_time"])+";"
        if attributes["ms_availability"]:
            service_formulas="\nformula ms_availability = "+str(attributes["ms_availability"])+";"
        service_formulas="\nformula cost = 0;\nformula performance = 0;\n/>" # En microservicio clásico sería cost y performance
        service_instance = service_instance + service_formulas
        logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE COMPLETED")
        services = services + service_instance + "\n"
        if attributes["selected_cpu"]:
            for machine_pair in attributes["selected_cpu"]:
                machine_name, machine_characteristics = machine_pair
                if machine_name not in processed_machines:
                    processed_machines.append(machine_name)
                    machine_instance = "sig "+machine_name+" extends CPU {}\n"
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE CREATED")
                    machine_formulas = "</"
                    for characteristic in machine_characteristics.items():
                        machine_formulas=machine_formulas+"\nformula "+characteristic+" = "+machine_characteristics[characteristic]+";"
                    machine_formulas = machine_formulas+"\n/>"
                    machine_instance = machine_instance + machine_formulas
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE COMPLETED")
                    machines = machines + machine_instance+"\n" 
    return machines, services

def quantum_generator_string(candidates):
    services = ""
    machines = ""
    processed_machines = []
    for service_name, attributes in candidates.items():
        service_instance = "one "+service_name+" extends "+service_name.capitalize()+" {}\n"
        logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE CREATED")
        service_formulas = "</"
        if attributes["shots"]:
            service_formulas="\nformula shots = "+str(attributes["shots"])+";"
        service_formulas="\nformula cost = 0;\n/>" # En microservicio clásico sería cost y performance
        service_instance = service_instance + service_formulas
        logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE COMPLETED")
        services = services + service_instance + "\n"
        if attributes["selected_qpu"]:
            for machine_pair in attributes["selected_qpu"]:
                machine_name, machine_characteristics = machine_pair
                if machine_name not in processed_machines:
                    processed_machines.append(machine_name)
                    machine_instance = "sig "+machine_name+" extends QPU {}\n"
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE CREATED")
                    machine_formulas = "</"
                    for characteristic in machine_characteristics.items():
                        machine_formulas=machine_formulas+"\nformula "+characteristic+" = "+machine_characteristics[characteristic]+";"
                    machine_formulas = machine_formulas+"\n/>"
                    machine_instance = machine_instance + machine_formulas
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE COMPLETED")
                    machines = machines + machine_instance+"\n" 
    return machines, services


def generating_haiq_file():
    global behavioural, cpu_candidates, qpu_candidates
    qpu_machines, qpu_services = quantum_generator_string(qpu_candidates)
    cpu_machines, cpu_services = classical_generator_string(cpu_candidates)
    # Concatenar todo
    architectural_style_string = ""
    with open("./architectural_model/hybrid_app", 'r') as architectural_model_file:
        architectural_style_string = architectural_model_file.read()
    # String (behavioural) DEBE VENIR YA COMO STRING CUANDO SE LEE DE KAFKA
    file_string = architectural_style_string + behavioural + qpu_machines + cpu_machines + qpu_services + cpu_services
    # Guardar string como archivo .haiq en carpeta ./temp
    with open("./temp/hybrid-iot.haiq","w") as haiq_file:
        haiq_file.write(file_string)
            
if __name__=='__main__':
    logging.basicConfig(filename='file-generator.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    consumer = KafkaConsumer(
    TOPIC_BEHAVIOURAL, TOPIC_CPU_CANDIDATES, TOPIC_QPU_CANDIDATES,
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logging.debug("FILE-GENERATOR : INITIALIZED")
    processing_topics()
    generating_haiq_file()