"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Proceso encargado de procesar la información de los archivos de especificaciones
y distribuirla a los servicios (QPU_Selector o CPU_Selector) según corresponda.
"""
from flask import Flask
import requests


FOLDER_NAME = "deployment_app_folder"

app = Flask(__name__)


@app.route('/')
# Function to describe the status of the service
def index():
    return "ONLINE"


@app.route('/start')
def start_processing():
    """
    # leer archivo .zip
    # descomprimir en carpeta máquina local
    # leer archivos principales
    # leer archivos de requirements
    # Crear JSON de cuánticos
    # Crear JSON de clásicos
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