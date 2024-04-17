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
from config.config import OPEN_API_SPECIFICATION_PATH, MICROSERVICES_REQUIREMENTS_PATH, MICROSERVICE_QUANTUM_MODE, KAFKA_SERVER_URL, TOPIC_CPU, TOPIC_QPU
import logging
import os
import yaml
import json


FOLDER_NAME = "deployment_app_folder"

app = Flask(__name__)


@app.route('/')
# Function to describe the status of the service
def index():
    logging.debug("REQUEST / --> STATUS ONLINE")
    return "ONLINE"


@app.route('/start', methods=['POST'])
# Function to start the process of evaluating the hybrid application. It will produce a message for each consumer (QPU and CPU modules)
def start_processing():
    logging.debug("REQUEST RECIEVED --> /start")
    print("REQUEST RECIEVED --> /start")
    extract_path_app = "./app"
    qpu_services = dict() # CREATING DICTIONARY FOR QUANTUM SERVICES
    cpu_services = dict() # CREATING DICTIONARY FOR CLASSIC SERVICES
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
            zipfile[0].save(app_zip_file_path)
            logging.debug("REQUEST /start --> ZIP SAVED")
            logging.debug("REQUEST /start --> PROCESSING ZIP FILE")
            with ZipFile(app_zip_file_path, 'r') as zip: # EXTRACTING FILES FROM RECIEVED ZIP
                zip.extractall(absolute_path)
                logging.debug("ZIP FILE UNZIPPED")
            
            #app_oas_file_directory = extract_path_app+OPEN_API_SPECIFICATION_PATH # DIRECTORY OF OPEN API SPECIFICATIONS FILES
            #app_req_file_directory = app_zip_file_path + "/"+uploaded_file.name + MICROSERVICES_REQUIREMENTS_PATH # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
            app_req_file_directory = current_directory + name # DIRECTORY OF MICROSERVICES REQUIREMENTS FILES
            #app_oas_files = os.listdir(app_oas_file_directory)
            print("LECTURA DIRECTORIO")
            app_req_files = os.listdir(app_req_file_directory)
            print("DIRECTORIO LEIDO")
            print(app_req_files)
            logging.debug("REQUEST /start --> OAS DIRECTORY ACHIEVED")
            """
            for req_file_name in app_req_files: # ITERATING OVER OPEN API SPECIFICATIONS FILES
                print("REQUIREMENTS FILE PROCESSING")
                logging.debug("REQUEST /start --> OAS FILE PROCESSING INITIALIZED")
                req_file = os.path.join(app_req_file_directory, req_file_name)
                if os.path.isfile(req_file):
                    with open(req_file, 'r') as yaml_file: # PROCESSING YAML FILE
                        print("READING REQ FILE")
                        req_content = yaml.safe_load(yaml_file)
                        microservice_dict = dict()
                        microservice_dict["id"] = app_req_files.index(req_file_name) # CREATING ID FOR THE MICROSERVICE JSON 
                        if req_content["context"]["mode"]: # READING MICROSERVICE MODE
                            microservice_dict["mode"] = req_content["context"]["mode"]
                        logging.debug("REQUEST /start --> LOADING CLASSICAL REQUIREMENTS OF THE MICROSERVICE")
                        if req_content["behaviour"]["requests"]: # READING REQUIREMENTS ATTRIBUTE
                            microservice_dict["requests"] = req_content["behaviour"]["requests"]
                            logging.debug("REQUEST /start --> REQUESTS LOADED")
                        if req_content["behaviour"]["execution_time"]: # READING EXECUTION TIME ATTRIBUTE
                            microservice_dict["execution_time"] = req_content["behaviour"]["execution_time"]
                            logging.debug("REQUEST /start --> EXECUTION_TIME LOADED") 
                        if req_content["minimum_hw_req"]["cpu"]: # READING CPU ATTRIBUTE
                            microservice_dict["cpu"] = req_content["minimum_hw_req"]["cpu"]
                            logging.debug("REQUEST /start --> CPU LOADED") 
                        if req_content["minimum_hw_req"]["ram"]: # READING RAM ATTRIBUTE
                            microservice_dict["ram"] = req_content["minimum_hw_req"]["ram"]
                            logging.debug("REQUEST /start --> RAM LOADED")
                        cpu_services[req_file_name] = microservice_dict
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
                            qpu_services[req_file_name] = quantum_microservice
                            logging.debug("REQUEST /start --> QPU SERVICES UPDATED")
            #producer.send(TOPIC_QPU, qpu_services) # SENDIGN QUANTUM SERVICES JSON
            print("SENDIGN QUANTUM SERVICES JSON")
            logging.debug("REQUEST /start --> QUANTUM SERVICES JSON SEND")
            #producer.send(TOPIC_CPU, cpu_services) # SENDING CLASSICAL SERVICES JSON
            print("SENDIGN CLASSICAL SERVICES JSON")
            logging.debug("REQUEST /start --> CLASSICAL SERVICES JSON SEND")
            """            
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
    app.run(host="127.0.0.1", port=8586,debug=True)
    