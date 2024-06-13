from kafka import KafkaConsumer
from config.config import KAFKA_SERVER_URL, TOPIC_QPU_CANDIDATES, TOPIC_CPU_CANDIDATES, TOPIC_BEHAVIOURAL
import json
import logging
import os

behavioural_restrictions = None
cpu_candidates = None
qpu_candidates = None

def processing_topics():
    print("Waiting for topics")
    global behavioural_restrictions, cpu_candidates, qpu_candidates
    # Procesar mensajes de los topics
    logging.debug("FILE-GENERATOR : WAITING FOR MESSAGES")
    for message in consumer:
        logging.debug("FILE-GENERATOR : MESSAGE RECIEVED")
        topic = message.topic
        if topic == TOPIC_BEHAVIOURAL:
            # Procesando Behavioural File
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC BEHAVIOURAL")
            behavioural_restrictions = message.value
            behavioural = behavioural_restrictions['behavioural'] # POSIBLE ERROR PORQUE VENDRAN CON 2 ATTRIBUTOS BEHAVIOURAL Y RESTRICTIONS
            restrictions = behavioural_restrictions['restrictions']
            with open('./temp/behavioural.txt', 'w') as f:
                f.write(behavioural)
            with open('./temp/restrictions.txt', 'w') as f:
                f.write(restrictions)
            print(f"Procesado mensaje de archivo desde topic3 y guardado como received_file")
        elif topic == TOPIC_CPU_CANDIDATES:
            # Procesando CPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC CPU CANDIDATES")
            cpu_candidates = message.value
            print(f"Procesado mensaje JSON 1 desde topic1: {cpu_candidates}")
        elif topic == TOPIC_QPU_CANDIDATES:
            # Procesando QPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC QPU CANDIDATES")
            qpu_candidates = message.value
            print(f"Procesado mensaje JSON 2 desde topic2: {qpu_candidates}")
        if behavioural_restrictions != None and cpu_candidates != None and qpu_candidates!=None:
            # Una vez leidas las 3,salgo
            print("3 topics recieved")
            break
    consumer.close()


def classical_generator_string(candidates):
    services = ""
    machines = ""
    cloud_provider_cpu_machines = [] # Debe contener solo los nombres de las máquinas
    machine_services_restrictions = []
    processed_machines = []
    logging.debug("FILE-GENERATOR : CLASSICAL GENERATOR STRING")
    # Inicializar cloud provider machines
    for service_name, attributes in candidates.items():
        not_used_machines = cloud_provider_cpu_machines.copy() # Por cada servicio me creo una copia 
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
        if attributes["selected_cpus"]:
            for machine_array in attributes["selected_cpus"]:
                machine_name =  machine_array[0]
                machine_characteristics = machine_array[1]
                # Elimino la máquina de la copia 
                machine_services_restrictions.remove(machine_name)
                if machine_name not in processed_machines:
                    processed_machines.append(machine_name)
                    machine_instance = "sig "+machine_name+" extends CPU {}\n"
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE CREATED")
                    machine_formulas = "</"
                    for characteristic in machine_characteristics.items():
                        print("CARACTERÍSTICAS")
                        print(characteristic)
                        machine_formulas=machine_formulas+"\nformula "+characteristic+" = "+machine_characteristics[characteristic]+";"
                    machine_formulas = machine_formulas+"\n/>"
                    machine_instance = machine_instance + machine_formulas
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE COMPLETED")
                    machines = machines + machine_instance+"\n"
            # Coleccionar cada máquina del servicio
            # recorrer las máquinas disponibles del proveedor
            # si no está creo restricción
            machine_services_restrictions.append(service_name,not_used_machines) # Conjunto de pares servicio con máquinas no usadas \ 
            #para especificar las 
    return machines, services, machine_services_restrictions

def quantum_generator_string(candidates):
    services = ""
    machines = ""
    machine_services_restrictions = []
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
        if attributes["selected_qpus"]:
            for machine_array in attributes["selected_qpus"]:
                machine_name =  machine_array[0]
                machine_characteristics = machine_array[1]
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
    return machines, services, machine_services_restrictions

def machine_restriction(l):
    print("MACHINE RESTRICTION")
    result = ""
    for pair in l:
        service_name, machine_list = pair
        result = ' and '.join([f'"#({service_name} & {item}) = 0"' for item in machine_list])
        result = "all s:"+service_name+" | " + result
        restriction = restriction + "\n"+ result

def predicate_and_properties(use_case_restrictions, quantum, classical):
    print("PREDICATE")
    properties = "run show for 25\n\
        label done [some UseCase:workflowDone=true]\n\
        property rangeR{" + 'performanceRew' + "}[F done] totalPerformance;\n\
        property rangeR{" + 'costRew' + "}[F done] as totalCost;\n\
        property SminR{" + 'performanceRew' + "}[F done]\n\
        property SminR{" + 'costRew' + "}[F done]"
    quantum_machine_restriction = machine_restriction(quantum)
    classical_machine_restriction = machine_restriction(classical)
    predicate = "pred show {\n" + use_case_restrictions + quantum_machine_restriction + classical_machine_restriction + "\n}\n"
    return (predicate + properties)

def haiq_file_generator():
    global cpu_candidates, qpu_candidates
    qpu_machines, qpu_services, quantum = quantum_generator_string(qpu_candidates)
    cpu_machines, cpu_services, classical = classical_generator_string(cpu_candidates)
    # Concatenar todo
    architectural_style_string = ""
    print("HAIQ GENERATOR")
    with open("./architectural_specification/quantum-classical-app.als", 'r') as architectural_model_file:
        architectural_style_string = architectural_model_file.read()
    with open("./temp/behavioural.txt", 'r') as architectural_model_file:
        behavioural_string = architectural_model_file.read()
    with open("./temp/restrictions.txt", 'r') as architectural_model_file:
        restrictions_string = architectural_model_file.read()
    # String (behavioural) DEBE VENIR YA COMO STRING CUANDO SE LEE DE KAFKA
    file_string = architectural_style_string + behavioural_string + predicate_and_properties(restrictions_string,quantum,classical) + qpu_machines + cpu_machines + qpu_services + cpu_services
    # Guardar string como archivo .haiq en carpeta ./temp
    with open("./temp/hybrid-iot.haiq","w") as haiq_file:
        haiq_file.write(file_string)
            
if __name__=='__main__':
    print("FILE GENERATOR ON")
    logging.basicConfig(filename='file-generator.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logging.debug("FILE-GENERATOR : INITIALIZED")
    # Faltaría un while true para que vaya iterando
    consumer.subscribe([TOPIC_BEHAVIOURAL, TOPIC_CPU_CANDIDATES, TOPIC_QPU_CANDIDATES])
    processing_topics()
    haiq_file_generator()