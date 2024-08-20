"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informática
Universidad de Málaga
Descripcion:
- Cliente Web --> Proporciona una interfaz gráfica donde subir las especificaciones.
"""

from flask import Flask, render_template, request
import requests
import os
import logging
from config.config import INFORMATION_PROCESSING_URL


app = Flask(__name__)

configurations_list = None

@app.route('/')
def index():
    logging.debug("REQUEST / --> RENDERING TEMPLATE")
    global configurations_list
    configurations_list = None
    return render_template('home.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    global configurations_list
    data = request.get_json()

    if data:
        configurations_list = data
    return jsonify({"status": "success", "message": "Data received"}), 200



@app.route('/upload', methods=['POST'])
def upload_file():
    logging.debug("REQUEST /upload --> STARTS")
    if 'file' not in request.files:
        logging.debug("REQUEST /upload --> NO FILE SELECTED")
        info_message = 'No file has been selected. Please reload the page.'
        return render_template('home.html', info_message=info_message), 400
    file = request.files['file']
    if file.filename == '':
        logging.debug("REQUEST /upload --> NO FILE SELECTED")
        info_message = 'No file has been selected. Please reload the page.'
        return render_template('home.html', info_message=info_message), 400

    
    if file and file.filename.endswith('.zip') and request.form['cost'] and request.form['performance']:
        # Guarda el archivo en el servidor temporalmente
        print("INFORMATION FROM FORM RECIEVED CORRECTLY")
        filename = file.filename
        file.save(os.getcwd()+"/temp/"+filename)
        cost_weight = float(request.form['cost'])
        performance_weight = float(request.form['performance'])
        cost_and_performance = {'cost_weight': cost_weight, 'performance_weight' : performance_weight}
        # Envía el archivo al microservicio
        try:
            url = INFORMATION_PROCESSING_URL+"/start"
            print(cost_and_performance)
            files = {filename: open(os.getcwd()+"/temp/"+filename, 'rb')}
            response = requests.post(url, files=files, data=cost_and_performance)
            if response.status_code == 200:
                # Eliminar archivo temporal
                info_message = "Information was correctly send. The process has started."
                return render_template('progress.html', info_message=info_message), 500
            else:
                error_message = 'An error processing the information happened. Please, restart the process.'
                return render_template('error.html', error_message=error_message), 500
        except Exception as e:
            error_message = 'An exception has been launched\n' + e
            return render_template('error.html', error_message=error_message), 500
            
    else:
        logging.debug("REQUEST /upload --> NO ZIP FILE SELECTED")
        return 'El archivo no es un archivo .zip válido', 400

if __name__ == '__main__':
    logging.basicConfig(filename=os.getcwd()+'/web.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    #app.run(host="127.0.0.1", port=8585,debug=True)
    app.run(host="0.0.0.0", port=8585,debug=True)
