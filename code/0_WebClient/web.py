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
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No se ha seleccionado ningún archivo', 400

    file = request.files['file']

   
    if file.filename == '':
        return 'No se ha seleccionado ningún archivo', 400

    
    if file and file.filename.endswith('.zip'):
        # Guarda el archivo en el servidor temporalmente
        filename = file.filename
        filepath = os.path.join('temp', filename)
        file.save(filepath)

        # Envía el archivo al microservicio
        try:
            url = 'http://processing_information/start'
            files = {'file': open(filepath, 'rb')}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                # Eliminar archivo temporal
                return 'El archivo se ha enviado correctamente al microservicio'
            else:
                return 'Ocurrió un error al enviar el archivo al microservicio', 500
        except Exception as e:
            return f'Ocurrió un error: {str(e)}', 500
    else:
        return 'El archivo no es un archivo .zip válido', 400

if __name__ == '__main__':
    logging.basicConfig(filename='web.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    app.run(host="127.0.0.1", port=8585,debug=True)

