from kafka import KafkaConsumer, KafkaProducer
from config.config import KAFKA_SERVER_URL, TOPIC_QPU_CANDIDATES, TOPIC_CPU_CANDIDATES, TOPIC_BEHAVIOURAL, HAIQ_MANAGER_URL, TOPIC_WEB
import json
import logging
import os
import requests

behavioural_restrictions = None
cpu_candidates = None
qpu_candidates = None

def processing_topics():
    print("WAITING FOR TOPICS")
    global behavioural_restrictions, cpu_candidates, qpu_candidates
    # Procesar mensajes de los topics
    logging.debug("FILE-GENERATOR : WAITING FOR MESSAGES")
    for message in consumer:
        logging.debug("FILE-GENERATOR : MESSAGE RECIEVED")
        topic = message.topic
        if topic == TOPIC_BEHAVIOURAL:
            # Procesando Behavioural File
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC BEHAVIOURAL")
            print(f"PROCESSED MESSAGE FROM TOPIC: {topic}")
            behavioural_restrictions = message.value
            behavioural = behavioural_restrictions['behavioural'] # POSIBLE ERROR PORQUE VENDRAN CON 2 ATTRIBUTOS BEHAVIOURAL Y RESTRICTIONS
            restrictions = behavioural_restrictions['restrictions']
            with open('./temp/behavioural.txt', 'w', encoding='utf-8') as f:
                f.write(behavioural)
            with open('./temp/restrictions.txt', 'w', encoding='utf-8') as f:
                f.write(restrictions)
            logging.debug("FILE-GENERATOR : BEHAVIORAL AND RESTRICTIONS SAVED SUCCESSFULLY")
        elif topic == TOPIC_CPU_CANDIDATES:
            # Procesando CPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC CPU CANDIDATES")
            cpu_candidates = message.value
            print(f"PROCESSED MESSAGE FROM TOPIC: {topic}")
        elif topic == TOPIC_QPU_CANDIDATES:
            # Procesando QPUs
            logging.debug("FILE-GENERATOR : MESSAGE FROM TOPIC QPU CANDIDATES")
            qpu_candidates = message.value
            print(f"PROCESSED MESSAGE FROM TOPIC: {topic}")
        if behavioural_restrictions != None and cpu_candidates != None and qpu_candidates!=None:
            # Una vez leidas las 3,salgo
            print("MESSAGES RECIEVED, STARTING FILE GENERATOR")
            producer.send(TOPIC_WEB, "HAIQ_FILE_GENERATOR")
            producer.flush()
            haiq_file_generator()


def classical_generator_string(candidates):
    services = ""
    machines = ""
    cloud_provider_cpu_machines = [] # Debe contener solo los nombres de las máquinas
    machine_services_restrictions = []
    processed_machines = []
    logging.debug("FILE-GENERATOR : CLASSICAL GENERATOR STRING")
    # Inicializar cloud provider machines
    cloud_providers_path = "./cpu-cloud-providers"
    cloud_providers_list = os.listdir(cloud_providers_path)
    for cloud_provider in cloud_providers_list:
        cloud_provider_file = os.path.join(cloud_providers_path+"/"+cloud_provider)
        if os.path.isfile(cloud_provider_file):
            cpu_machines = None
            with open(cloud_provider_file, 'r') as f:
                logging.debug(" CPU MACHINES READING")
                cpu_machines = json.load(f)
            for cpu_machine, machine_information in cpu_machines.items():
                cloud_provider_cpu_machines.append(cpu_machine.replace(".","_"))
    for service_name, attributes in candidates.items():
        not_used_machines = cloud_provider_cpu_machines.copy() # Por cada servicio me creo una copia
        for instance_number in range(int(attributes["ms_instances"])):
            if attributes["ms_mandatory"]:
                value = attributes["ms_mandatory"]
                if value:
                    # The service is mandatory so it would be one
                    service_instance = "one sig "+service_name+"_"+str(instance_number)+" extends "+service_name.capitalize()+" {}\n"
                else:
                    # The service isn't mandatory so it would be lone
                    service_instance = "lone sig "+service_name+"_"+str(instance_number)+" extends "+service_name.capitalize()+" {}\n"
            logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE CREATED")
            service_formulas = "</"
            if attributes["ms_logical_performance_factor"]:
                service_formulas= service_formulas + "\nformula ms_logical_performance_factor = "+str(attributes["ms_logical_performance_factor"])+";"
            if attributes["ms_ram"]:
                service_formulas=service_formulas + "\nformula ms_ram = "+str(attributes["ms_ram"])+";"
            if attributes["ms_bandwidth"]:
                service_formulas=service_formulas +"\nformula ms_bandwidth = "+str(attributes["ms_bandwidth"])+";"
            if attributes["ms_execution_time"]:
                service_formulas=service_formulas +"\nformula ms_execution_time = "+str(attributes["ms_execution_time"])+";"
            if attributes["ms_availability"]:
                service_formulas=service_formulas +"\nformula ms_availability = "+str(attributes["ms_availability"])+";"
            service_formulas=service_formulas +"\nformula cost = 0;\nformula performance = 0;\n/>" # En microservicio clásico sería cost y performance
            service_instance = service_instance + service_formulas
            logging.debug("FILE-GENERATOR : CLASSICAL SERVICE INSTANCE COMPLETED")
            services = services + service_instance + "\n"
        # Finish processing instances
        if attributes["selected_cpus"]:
            for machine_array in attributes["selected_cpus"]:
                machine_name =  machine_array[0]
                machine_characteristics = machine_array[1]
                # Elimino la máquina de la lista de todas las máquinas del servicio
                not_used_machines.remove(machine_name)
                if machine_name not in processed_machines:
                    processed_machines.append(machine_name)
                    machine_instance = "sig "+machine_name+" extends CPU {}\n"
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE CREATED")
                    machine_formulas = "</"
                    for characteristic in machine_characteristics.items():
                        machine_formulas=machine_formulas+"\nformula "+characteristic[0]+" = "+str(characteristic[1])+";"
                    machine_formulas = machine_formulas+"\n[services:cpair] true -> true;\n/>"
                    machine_instance = machine_instance + machine_formulas
                    logging.debug("FILE-GENERATOR : CLASSICAL MACHINE INSTANCE COMPLETED")
                    machines = machines + machine_instance+"\n"
            # Coleccionar cada máquina del servicio
            # recorrer las máquinas disponibles del proveedor
            # si no está creo restricción
            machine_services_restrictions.append(tuple((service_name,not_used_machines))) # Conjunto de pares servicio con máquinas no usadas \ 
            #para especificar las 
            # Devuelve todas las máquinas que se han puesto y esto es usado para generar las restricciones y no generar restricciones de máquinas que no se han puesto
    return machines, services, machine_services_restrictions, processed_machines

def quantum_generator_string(candidates):
    services = ""
    machines = ""
    cloud_provider_qpu_machines = []
    machine_services_restrictions = []
    processed_machines = []
    cloud_providers_path = "./qpu-cloud-providers"
    cloud_providers_list = os.listdir(cloud_providers_path)
    for cloud_provider in cloud_providers_list:
        cloud_provider_file = os.path.join(cloud_providers_path+"/"+cloud_provider)
        if os.path.isfile(cloud_provider_file):
            qpu_machines = None
            with open(cloud_provider_file, 'r') as f:
                logging.debug("QPU MACHINES READING")
                qpu_machines = json.load(f)
            for qpu_machine, machine_information in qpu_machines.items():
                cloud_provider_qpu_machines.append(qpu_machine.replace(".","_"))
    for service_name, attributes in candidates.items():
        not_used_machines = cloud_provider_qpu_machines.copy()
        #Para los cuánticos, su instancia es única
        if attributes["mandatory"]:
                value = attributes["ms_mandatory"]
                if value:
                    # The service is mandatory so it would be one
                    service_instance = "one sig "+service_name+" extends "+"Quantum_"+service_name.capitalize()+" {}\n"
                else:
                    # The service isn't mandatory so it would be lone
                    service_instance = "lone sig "+service_name+" extends "+"Quantum_"+service_name.capitalize()+" {}\n"
        logging.debug("FILE-GENERATOR : QUANTUM SERVICE INSTANCE CREATED")
        service_formulas = "</"
        if attributes["shots"]:
            service_formulas= service_formulas + "\nformula shots = "+str(attributes["shots"])+";"
        service_formulas= service_formulas + "\nformula cost = 0;\n/>" # En microservicio clásico sería cost y performance
        service_instance = service_instance + service_formulas
        logging.debug("FILE-GENERATOR : QUANTUM SERVICE INSTANCE COMPLETED")
        services = services + service_instance + "\n"
        if attributes["selected_qpus"]:
            for machine_array in attributes["selected_qpus"]:
                machine_name =  machine_array[0]
                machine_characteristics = machine_array[1]
                not_used_machines.remove(machine_name)
                if machine_name not in processed_machines:
                    processed_machines.append(machine_name)
                    machine_instance = "sig "+machine_name+" extends QPU {}\n"
                    logging.debug("FILE-GENERATOR : QUANTUM MACHINE INSTANCE CREATED")
                    machine_formulas = "</"
                    for characteristic in machine_characteristics.items():
                        machine_formulas=machine_formulas+"\nformula "+characteristic[0]+" = "+str(characteristic[1])+";"
                    machine_formulas = machine_formulas+"\n[services:qpair] true -> true;\n/>"
                    machine_instance = machine_instance + machine_formulas
                    machines = machines + machine_instance+"\n"
                    logging.debug("FILE-GENERATOR : QUANTUM MACHINE INSTANCE COMPLETED")
            machine_services_restrictions.append(tuple((service_name,not_used_machines)))
    return machines, services, machine_services_restrictions, processed_machines

def machine_restriction(l, used):
    result = ""
    restriction = ""
    for pair in l:
        service_name, machine_list = pair
        result = ' and '.join([f'#({service_name.capitalize()} & {item}) = 0' for item in machine_list if item in used])
        if result:
            result = "all s:"+service_name.capitalize()+" | " + result
            restriction = restriction + result + "\n"
        result = ""
    return restriction

def predicate_and_properties(use_case_restrictions, quantum, classical, quantum_used, classical_used):
    properties = "run show for 25\n\
label done [some UseCase:workflowDone=true]\n\
property rangeR{" + 'performanceRew' + "}[F done] totalPerformance;\n\
property rangeR{" + 'costRew' + "}[F done] as totalCost;\n\
property SminR{" + 'performanceRew' + "}[F done]\n\
property SminR{" + 'costRew' + "}[F done]\n"
    quantum_machine_restriction = machine_restriction(quantum, quantum_used)
    classical_machine_restriction = machine_restriction(classical, classical_used)
    predicate = "\npred show {\n" + use_case_restrictions + quantum_machine_restriction + classical_machine_restriction + "\n}\n"
    return (predicate + properties)

def haiq_file_generator():
    global cpu_candidates, qpu_candidates, behavioural_restrictions
    print("HAIQ GENERATOR STARTED")
    qpu_machines, qpu_services, quantum, quantum_used_machines = quantum_generator_string(qpu_candidates)
    cpu_machines, cpu_services, classical, classical_used_machines = classical_generator_string(cpu_candidates)
    # Concatenar todo
    architectural_style_string = ""
    with open("./architectural_specification/quantum-classical-app.als", 'r', encoding='utf-8') as architectural_model_file:
        architectural_style_string = architectural_model_file.read()
    with open("./temp/behavioural.txt", 'r', encoding='utf-8') as architectural_model_file:
        behavioural_string = architectural_model_file.read()
    with open("./temp/restrictions.txt", 'r', encoding='utf-8') as architectural_model_file:
        restrictions_string = architectural_model_file.read()
    # String (behavioural) DEBE VENIR YA COMO STRING CUANDO SE LEE DE KAFKA
    file_string = architectural_style_string + behavioural_string + predicate_and_properties(restrictions_string, quantum, classical, quantum_used_machines, classical_used_machines) + qpu_machines + cpu_machines + qpu_services + cpu_services
    # Guardar string como archivo .haiq en carpeta ./temp
    with open("./temp/hybrid-iot.haiq","w", encoding='utf-8') as haiq_file:
        haiq_file.write(file_string)
    print("HAIQ FILE GENERATED")
    logging.debug("FILE-GENERATOR : HAIQ FILE GENERATED")
    # Enviar archivo a HaiqLauncher
    producer.send(TOPIC_WEB, "HAIQ_ANALYSIS")
    producer.flush()
    url = HAIQ_MANAGER_URL+"/launch-haiq"
    files = {"haiqFile": open(os.getcwd()+"/temp/"+"hybrid-iot.haiq", 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print("HAIQ RESULT SUCCESSFULLY SENT TO HAIQ LAUNCHER")
        logging.debug("FILE-GENERATOR : HAIQ RESULT SUCCESSFULLY SENT")
        behavioural_restrictions = None
        cpu_candidates = None
        qpu_candidates = None
        logging.debug("FILE-GENERATOR : RESET VARs")
    else:
        print("SOMETHING WAS WRONG WHILE SENDING HAIQ FILE TO HAIQ LAUNCHER")
        logging.debug("FILE-GENERATOR : HAIQ RESULT SENT ERROR")

            
if __name__=='__main__':
    print("FILE GENERATOR ON")
    logging.basicConfig(filename='file-generator.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logging.debug("FILE-GENERATOR : INITIALIZED")
    # Faltaría un while true para que vaya iterando
    consumer.subscribe([TOPIC_BEHAVIOURAL, TOPIC_CPU_CANDIDATES, TOPIC_QPU_CANDIDATES])
    processing_topics()
    