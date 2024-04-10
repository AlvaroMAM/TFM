"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Proceso encargado de procesar la información de los archivos de especificaciones
y distribuirla a los servicios (QPU_Selector o CPU_Selector) según corresponda.
"""
from flask import Flask, request
from zipfile import ZipFile
import requests
import logging


FOLDER_NAME = "deployment_app_folder"

app = Flask(__name__)


@app.route('/')
# Function to describe the status of the service
def index():
    return "ONLINE"


@app.route('/start', methods=['POST'])
def start_processing():
    qpu_services = {}
    cpu_services = {}
    if request.files:
        uploaded_file = request.files[0] #Leo archivo zip ( ImmutableMultiDict[str, FileStorage])
        print(type(uploaded_file))
        app_zip_file = uploaded_file[1]
        with ZipFile(app_zip_file, 'r') as zip: 
            zip.extractall() 
            logging.debug("ZIP FILE UNZIPPED") 

    """
    # Inicializar JSON de cuánticos ✅
    # Inicializar JSON de clásicos ✅
    # leer archivo .zip ✅
    # descomprimir en carpeta máquina local ✅
    # leer archivos principales
    # Procesar archivo a archivo y leer sus requirements, en el caso de que en los requirements el type sea cuántico, 
    # entonces se añade al json de cuántico, o al de clásico si es de otro tipo.
    # El nombre a usar será el nombre del archivo principal sin yml.
    # leer archivos de requirements
    # Tomar los productores previamente creados en el main
    # Enviar los json a cada topic correspondiente
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
    logging.basicConfig(filename='information-processing.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')