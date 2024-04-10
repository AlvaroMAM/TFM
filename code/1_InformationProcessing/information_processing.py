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
from ..config.config import OPEN_API_SPECIFICATION_PATH, MICROSERVICES_REQUIREMENTS_PATH, MICROSERVICE_QUANTUM_MODE, KAFKA_SERVER_URL, TOPIC_CPU, TOPIC_QPU
import logging
import os
import yaml
import json


FOLDER_NAME = "deployment_app_folder"

app = Flask(__name__)


@app.route('/')
# Function to describe the status of the service
def index():
    return "ONLINE"


@app.route('/start', methods=['POST'])
# Function to start the process of evaluating the hybrid application. It will produce a message for each consumer (QPU and CPU modules)
def start_processing():
    logging.debug("REQUEST RECIEVED --> /start")
    extract_path_app = "./app"
    qpu_services = dict() # CREATING DICTIONARY FOR QUANTUM SERVICES
    cpu_services = dict() # CREATING DICTIONARY FOR CLASSIC SERVICES
    if request.files:
        logging.debug("REQUEST /start --> FILES RECIEVED")
        uploaded_file = request.files[0] # READING ZIP FILE FROM REQUEST ( ImmutableMultiDict[str, FileStorage])
        print(type(uploaded_file))
        app_zip_file = uploaded_file[1]
        logging.debug("REQUEST /start --> PROCESSING ZIP FILE")
        with ZipFile(app_zip_file, 'r') as zip: # EXTRACTING FILES FROM RECIEVED ZIP
            zip.extractall(extract_path_app) 
            logging.debug("ZIP FILE UNZIPPED")
        #app_oas_file_directory = extract_path_app+OPEN_API_SPECIFICATION_PATH # DIRECTORY OF OPEN API SPECIFICATIONS FILES
        app_req_file_directory = extract_path_app+MICROSERVICES_REQUIREMENTS_PATH # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
        #app_oas_files = os.listdir(app_oas_file_directory)
        app_req_files = os.listdir(app_req_file_directory)
        logging.debug("REQUEST /start --> OAS DIRECTORY ACHIEVED")
        for req_file_name in app_req_files: # ITERATING OVER OPEN API SPECIFICATIONS FILES
            logging.debug("REQUEST /start --> OAS FILE PROCESSING INITIALIZED")
            req_file = os.path.join(app_req_file_directory, req_file_name)
            if os.path.isfile(req_file):
                with open(req_file, 'r') as yaml_file: # PROCESSING YAML FILE
                    req_content = yaml.safe_load(yaml_file)
                    microservice_dict = dict()
                    microservice_dict["id"] = app_req_files.index(req_file_name) # CREATING ID FOR THE MICROSERVICE JSON 
                    if req_content["context"]["mode"]: # READING MICROSERVICE MODE
                        microservice_dict["mode"] = req_content["context"]["mode"]
                    logging.debug("REQUEST /start --> LOADING CLASSICAL REQUIREMENTS OF THE MICROSERVICE")
                    if req_content["requirements"]["requests"]: # READING REQUIREMENTS ATTRIBUTE
                        microservice_dict["requests"] = req_content["requirements"]["requests"]
                        logging.debug("REQUEST /start --> REQUESTS LOADED")
                    if req_content["requirements"]["execution_time"]: # READING EXECUTION TIME ATTRIBUTE
                        microservice_dict["execution_time"] = req_content["requirements"]["execution_time"]
                        logging.debug("REQUEST /start --> EXECUTION_TIME LOADED") 
                    if req_content["requirements"]["cpu"]: # READING CPU ATTRIBUTE
                        microservice_dict["cpu"] = req_content["requirements"]["cpu"]
                        logging.debug("REQUEST /start --> CPU LOADED") 
                    if req_content["requirements"]["ram"]: # READING RAM ATTRIBUTE
                        microservice_dict["ram"] = req_content["requirements"]["ram"]
                        logging.debug("REQUEST /start --> RAM LOADED")
                    cpu_services[req_file_name] = microservice_dict
                    logging.debug("REQUEST /start --> CPU SERVICES UPDATED") 
                    if microservice_dict["mode"] == MICROSERVICE_QUANTUM_MODE: # LOADING QUANTUM REQUIREMENTS OF THE MICROSERVICE
                        logging.debug("REQUEST /start --> LOADING QUANTUM REQUIREMENTS OF THE MICROSERVICE")
                        quantum_microservice = dict()
                        quantum_microservice["id"] = microservice_dict["id"]
                        if req_content["requirements"]["qubits"]: # READING QUBITS ATTRIBUTE
                            quantum_microservice["qubits"] = req_content["requirements"]["qubits"]
                            logging.debug("REQUEST /start --> QUBITS LOADED") 
                        if req_content["requirements"]["shots"]: # READING SHOTS ATTRIBUTE
                            quantum_microservice["shots"] = req_content["requirements"]["shots"]
                            logging.debug("REQUEST /start --> SHOTS LOADED")
                        #ADDING MICROSERVICES TO QUANTUM_JSON
                        qpu_services[req_file_name] = quantum_microservice
                        logging.debug("REQUEST /start --> QPU SERVICES UPDATED")
        producer.send(TOPIC_CPU, qpu_services) # SENDIGN QUANTUM SERVICES JSON
        logging.debug("REQUEST /start --> QUANTUM SERVICES JSON SEND")
        producer.send(TOPIC_QPU, cpu_services) # SENDING CLASSICAL SERVICES JSON
        logging.debug("REQUEST /start --> CLASSICAL SERVICES JSON SEND")
                    
        return Response("EVALUATION PROCESS LAUNCHED", status=200, mimetype='text/plain')

    else:
        logging.debug("REQUEST /start --> FILES NOT RECIEVED")
        return Response("SOMETHING WAS WRONG :(", status=500, mimetype='text/plain')
        

    """
    # Pregunta: ¿Qué hacer con la parte de evaluación de la parte clásica de los servicios cuánticos?
    # Que cada módulo evalúe la parte correspondiente y después en el generador de combinaciones los agrupo
    # generando un único json con la estrucutra
    app : {
        microservice_1: {
            cpu_machines : [],
            qpu_machines : []
        }, 
        ...
        microservice_n {
            cpu_machines : [],
            qpu_machines : []
        }
    }
    """
    return None



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8586,debug=True)
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    logging.basicConfig(filename='information-processing.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')