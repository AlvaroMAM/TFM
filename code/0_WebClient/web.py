"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:

- Cliente Web --> Proporciona una interfaz gráfica donde subir las especificaciones.
"""

from flask import Flask, render_template, request
import requests
import os
import logging



app = Flask(__name__)


@app.route('/')
def index():
    logging.debug("REQUEST / --> RENDERING TEMPLATE")
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("PETITION")
    logging.debug("REQUEST /upload --> STARTS")
    if 'file' not in request.files:
        print("NOT FILE")
        logging.debug("REQUEST /upload --> NO FILE SELECTED")
        return 'No se ha seleccionado ningún archivo', 400

    file = request.files['file']

   
    if file.filename == '':
        logging.debug("REQUEST /upload --> NO FILE SELECTED")
        return 'No se ha seleccionado ningún archivo', 400

    
    if file and file.filename.endswith('.zip'):
        # Guarda el archivo en el servidor temporalmente
        print("LLEGA ARCHIGO")
        filename = file.filename
        print(filename)
        print("LLEGA ARCHIGO")
        file.save("./temp"+filename)
        print("GUARDADO")

        # Envía el archivo al microservicio
        try:
            url = 'http://127.0.0.1:8586/start'
            files = {'file': open("./temp"+filename, 'rb')}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                # Eliminar archivo temporal
                return 'El archivo se ha enviado correctamente al microservicio'
            else:
                return 'Ocurrió un error al enviar el archivo al microservicio', 500
        except Exception as e:
            return f'Ocurrió un error: {str(e)}', 500
    else:
        logging.debug("REQUEST /upload --> NO ZIP FILE SELECTED")
        return 'El archivo no es un archivo .zip válido', 400

if __name__ == '__main__':
    logging.basicConfig(filename='web.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    app.run(host="127.0.0.1", port=8585,debug=True)

