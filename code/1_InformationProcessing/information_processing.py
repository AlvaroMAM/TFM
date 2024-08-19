"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Proceso encargado de procesar la información de los archivos de especificaciones
y distribuirla a los servicios (QPU_Selector o CPU_Selector) según corresponda.
"""
from flask import Flask, request, Response
from zipfile import ZipFile
from kafka import KafkaProducer
from config.config import OPEN_API_SPECIFICATION_PATH, MICROSERVICES_REQUIREMENTS_PATH, MICROSERVICES_MODEL_PATH, MICROSERVICE_QUANTUM_MODE, KAFKA_SERVER_URL, TOPIC_CPU, TOPIC_QPU, TOPIC_BEHAVIOURAL, TOPIC_HAIQ_RESULT, TOPIC_UTILITY_VALUES
import logging
import os
import yaml
import json


FOLDER_NAME = "deployment_app_folder"

COST_WEIGHT = None
PERFORMANCE_WEIGHT = None
app = Flask(__name__)


@app.route('/')
# Function to describe the status of the service
def index():
    logging.debug("REQUEST / --> STATUS ONLINE")
    return "ONLINE"

@app.route('/haiq-result', methods=['POST'])
def haiq_result():
    # Lectura de archivo de resultado de haiq
    logging.debug("REQUEST RECIEVED --> /haiq-result")
    data_recieved = None
    global COST_WEIGHT, PERFORMANCE_WEIGHT
    if request.files:
        data_recieved = request.files
        print(data_recieved)
        haiq_result = data_recieved['files']
        print("HAIQ RESULT SUCESSFULLY READ")
        logging.debug("REQUEST /haiq-result --> HAIQ RESULT SUCESSFULLY READ")
        # Envío por kafka a calculadora de utilidad
        if haiq_result:
            producer.send(TOPIC_HAIQ_RESULT, haiq_result)
            logging.debug("REQUEST /haiq-result --> HAIQ RESULT SUCESSFULLY SENT")
            # Envío por kafka de peso del coste y rendimiento a calculadora de utilidad
            json_utility = json.dumps(COST_WEIGHT, PERFORMANCE_WEIGHT)
            producer.send(TOPIC_UTILITY_VALUES,json_utility)
            logging.debug("REQUEST /haiq-result --> HAIQ WEIGHTS SUCESSFULLY SENT")
            # Reset variables: 
            COST_WEIGHT = None
            PERFORMANCE_WEIGHT = None
            return Response("Calculating utility", status=200, mimetype='text/plain')
        else:
            print("Something was wrong :(")
            logging.debug("REQUEST /haiq-result --> HAIQ RESULT READING WAS WRONG")
            return Response("Something was wrong during reading haiq_result", status=500, mimetype='text/plain')
    else:
        print("Something was wrong while reading request:(")
        logging.debug("REQUEST /haiq-result --> HAIQ RESULT READING WAS WRONG")
        return Response("Something was wrong during reading request", status=500, mimetype='text/plain')


@app.route('/start', methods=['POST'])
# Function to start the process of evaluating the hybrid application. It will produce a message for each consumer (QPU and CPU modules)
def start_processing():
    logging.debug("REQUEST RECIEVED --> /start")
    global COST_WEIGHT, PERFORMANCE_WEIGHT
    extract_path_app = "./app"
    qpu_services = dict() # CREATING DICTIONARY FOR QUANTUM SERVICES
    cpu_services = dict() # CREATING DICTIONARY FOR CLASSIC SERVICES
    print(request.form)
    recieved_utility_attributes = None
    print("PREVIO A LECTURA")
    recieved_utility_attributes = request.get_json()
    print(recieved_utility_attributes)
    if recieved_utility_attributes != None:
        print("NO EMPTY")
        COST_WEIGHT = recieved_utility_attributes.get('cost_weight')
        PERFORMANCE_WEIGHT = recieved_utility_attributes.get('performance_weight')
    else:
        return Response("SOMETHING WAS WRONG :(", status=500, mimetype='text/plain')
    if request.files:
        logging.debug("REQUEST /start --> FILES RECIEVED")
        name, zipfile = next(iter(request.files.to_dict(flat=False).items())) # READING ZIP FILE FROM REQUEST ( ImmutableMultiDict[str, FileStorage])
        # name is a string, zipfile is a list of FileStorage [FileStorage]
        if name == '':
            logging.debug("REQUEST /start --> FILES NOT RECIEVED")
            return Response("SOMETHING WAS WRONG :(", status=500, mimetype='text/plain')
        else:
            current_directory = os.getcwd()
            absolute_path = os.path.join(current_directory, "temp")
            if not os.path.exists(absolute_path):
                os.makedirs(absolute_path)
            app_zip_file_path = os.path.join(absolute_path, name)
            print("ZIP FILE PATH"+ app_zip_file_path)
            zipfile[0].save(app_zip_file_path)
            logging.debug("REQUEST /start --> ZIP SAVED")
            logging.debug("REQUEST /start --> PROCESSING ZIP FILE")
            with ZipFile(app_zip_file_path, 'r') as zip: # EXTRACTING FILES FROM RECIEVED ZIP
                zip.extractall(absolute_path)
                logging.debug("ZIP FILE UNZIPPED")
            #app_oas_file_directory = extract_path_app+OPEN_API_SPECIFICATION_PATH # DIRECTORY OF OPEN API SPECIFICATIONS FILES
            #app_req_file_directory = app_zip_file_path + "/"+uploaded_file.name + MICROSERVICES_REQUIREMENTS_PATH # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
            #app_req_file_directory = absolute_path + '/' + name.replace('.zip',"") + MICROSERVICES_REQUIREMENTS_PATH # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
            #app_model_file_directory = absolute_path + '/' + name.replace('.zip',"") + MICROSERVICES_MODEL_PATH 
            app_req_file_directory = absolute_path + MICROSERVICES_REQUIREMENTS_PATH # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
            app_model_file_directory = absolute_path + MICROSERVICES_MODEL_PATH 
            #app_oas_files = os.listdir(app_oas_file_directory)
            model_files = os.listdir(app_model_file_directory)
            behavioural_restrictions_dict = dict()
            for f in model_files:
                print("OPENED FILE: "+ f)
                with open(app_model_file_directory+"/"+f, 'r') as architectural_model_file:
                    behavioural_restrictions_dict[f] = architectural_model_file.read()
            print("ARCHITECTURAL FILES LOADED")
            producer.send(TOPIC_BEHAVIOURAL, behavioural_restrictions_dict)  
            logging.debug("REQUEST /start --> BEHAVIOURAL JSON SEND")
            app_req_files = os.listdir(app_req_file_directory)
            logging.debug("REQUEST /start --> OAS DIRECTORY ACHIEVED")
            for req_file_name in app_req_files: # ITERATING OVER OPEN API SPECIFICATIONS FILES
                print("PROCESSING FILE:"+req_file_name)
                logging.debug("REQUEST /start --> OAS FILE PROCESSING INITIALIZED")
                req_file = os.path.join(app_req_file_directory, req_file_name)
                if os.path.isfile(req_file):
                    with open(req_file, 'r') as yaml_file: # PROCESSING YAML FILE
                        req_content = yaml.safe_load(yaml_file)
                        microservice_dict = dict()
                        microservice_dict["id"] = app_req_files.index(req_file_name) # CREATING ID FOR THE MICROSERVICE JSON
                        if req_content["context"]["mode"]: # READING MICROSERVICE ID
                            microservice_name = req_content["context"]["id"]
                        logging.debug("REQUEST /start --> LOADING CLASSICAL REQUIREMENTS OF THE MICROSERVICE")
                        if req_content["context"]["mode"]: # READING MICROSERVICE MODE
                            microservice_dict["mode"] = req_content["context"]["mode"]
                        logging.debug("REQUEST /start --> LOADING CLASSICAL REQUIREMENTS OF THE MICROSERVICE")
                        if req_content["behaviour"]["requests"]: # READING REQUIREMENTS ATTRIBUTE
                            microservice_dict["number_requests"] = req_content["behaviour"]["requests"]["number_request"]
                            logging.debug("REQUEST /start --> NUMBER OF REQUESTS LOADED")
                            microservice_dict["maximum_request_size"] = req_content["behaviour"]["requests"]["maximum_request_size"]
                            logging.debug("REQUEST /start --> SIZE OF REQUESTS LOADED")
                        if req_content["behaviour"]["execution_time"]: # READING EXECUTION TIME ATTRIBUTE
                            microservice_dict["execution_time"] = req_content["behaviour"]["execution_time"]
                            logging.debug("REQUEST /start --> EXECUTION_TIME LOADED")
                        if req_content["behaviour"]["availability"]: # READING EXECUTION AVAILABILITY
                            microservice_dict["availability"] = req_content["behaviour"]["availability"]
                            logging.debug("REQUEST /start --> AVAILABILITY LOADED")
                        if req_content["behaviour"]["instances"]: # READING EXECUTION AVAILABILITY
                            microservice_dict["instances"] = req_content["behaviour"]["instances"]
                            logging.debug("REQUEST /start --> AVAILABILITY LOADED")   
                        if req_content["minimum_hw_req"]["cpu"]: # READING CPU ATTRIBUTE
                            microservice_dict["cpu"] = req_content["minimum_hw_req"]["cpu"]
                            logging.debug("REQUEST /start --> CPU LOADED") 
                        if req_content["minimum_hw_req"]["ram"]: # READING RAM ATTRIBUTE
                            microservice_dict["ram"] = req_content["minimum_hw_req"]["ram"]
                            logging.debug("REQUEST /start --> RAM LOADED")
                        cpu_services[microservice_name] = microservice_dict
                        logging.debug("REQUEST /start --> CPU SERVICES UPDATED") 
                        if microservice_dict["mode"] == MICROSERVICE_QUANTUM_MODE: # LOADING QUANTUM REQUIREMENTS OF THE MICROSERVICE
                            logging.debug("REQUEST /start --> LOADING QUANTUM REQUIREMENTS OF THE MICROSERVICE")
                            quantum_microservice = dict()
                            quantum_microservice["id"] = microservice_dict["id"]
                            if req_content["minimum_hw_req"]["qubits"]: # READING QUBITS ATTRIBUTE
                                quantum_microservice["qubits"] = req_content["minimum_hw_req"]["qubits"]
                                logging.debug("REQUEST /start --> QUBITS LOADED") 
                            if req_content["behaviour"]["shots"]: # READING SHOTS ATTRIBUTE
                                quantum_microservice["shots"] = req_content["behaviour"]["shots"]
                                logging.debug("REQUEST /start --> SHOTS LOADED")
                            #ADDING MICROSERVICES TO QUANTUM_JSON
                            qpu_services[microservice_name] = quantum_microservice
                            logging.debug("REQUEST /start --> QPU SERVICES UPDATED")
            print("SENDING QUANTUM SERVICES JSON")
            print(qpu_services)
            producer.send(TOPIC_QPU, qpu_services) # SENDIGN QUANTUM SERVICES JSON
            logging.debug("REQUEST /start --> QUANTUM SERVICES JSON SEND")
            print("SENDING CLASSICAL SERVICES JSON")
            print(cpu_services)
            producer.send(TOPIC_CPU, cpu_services) # SENDING CLASSICAL SERVICES JSON
            logging.debug("REQUEST /start --> CLASSICAL SERVICES JSON SEND")
            # SENDING MODEL FILE TO COMBINATIONS GENERATOR
                 
            return Response("EVALUATION PROCESS LAUNCHED", status=200, mimetype='text/plain')
    else:
        logging.debug("REQUEST /start --> FILES NOT RECIEVED")
        return Response("SOMETHING WAS WRONG :(", status=500, mimetype='text/plain')
        

    """
    # Cada módulo evalúa la parte correspondiente y después en el generador de combinaciones los agrupo
    # generando un único json con la estructura y las características de las máquinas
    app : {
        microservice_1: {
            cpu_machines : [{name: machine 1, cpu: x, ram: y, ...}],
            qpu_machines : [{{name: machine 1, qubits: j, shots: i, ...}}]
        }, 
        ...
        microservice_n {
            cpu_machines : [{name: machine 1, cpu: x, ram: y, ...}],
            qpu_machines : []
        }
    }
    """



if __name__ == '__main__':
    logging.basicConfig(filename=os.getcwd()+'/information-processing.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    #app.run(host="127.0.0.1", port=8586,debug=True)
    app.run(host="0.0.0.0", port=8586,debug=True)
    