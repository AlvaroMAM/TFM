"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informática
Universidad de Málaga
Descripcion:
- Cliente Web --> Proporciona una interfaz gráfica donde subir las especificaciones.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import logging
from config.config import INFORMATION_PROCESSING_URL, HAIQ_MANAGER_URL


app = Flask(__name__)

configurations_list = None
COST_WEIGHT = None
PERFORMANCE_WEIGHT = None
EVALUATION_STAGE = None

@app.route('/')
def index():
    logging.debug("REQUEST / --> RENDERING TEMPLATE")
    global configurations_list, COST_WEIGHT, PERFORMANCE_WEIGHT, EVALUATION_STAGE
    configurations_list = None
    COST_WEIGHT = None
    PERFORMANCE_WEIGHT = None
    EVALUATION_STAGE = None
    return render_template('home.html')


@app.route('/showResults', methods=['GET', 'POST'])
def showResults():
    global configurations_list, COST_WEIGHT, PERFORMANCE_WEIGHT
    if request.method == 'GET':
        # If get load html with the list in table
        haiq_url = HAIQ_MANAGER_URL + "/downloadsol"
        return render_template('showResults.html', configurations=configurations_list, cost_weight=str(COST_WEIGHT), performance_weight=str(PERFORMANCE_WEIGHT), haiq_url=haiq_url)
    elif request.method == 'POST':
        # If post, update configuration list
        if request.is_json:
            configurations_list =  request.get_json()
            print(configurations_list)
            print(type(configurations_list))
            return jsonify({"message": "Data recieved correctly"}), 200
        else:
            print("SOLUTION LIST IS EMPTY")
            return jsonify({"message": "Data recieved is empty"}), 500
    else:
        print("METHOD NOT SUPPORTED")
        error_message = 'Method not supported. Please restart the process'
        return render_template('error.html', error_message=error_message), 500
   
    


@app.route('/refresh', methods=['GET','POST'])
def refresh():
    global EVALUATION_STAGE
    if request.method == 'GET':
        return render_template('progress.html', evaluation_stage=EVALUATION_STAGE), 200
    elif request.method == 'POST':
        if request.form != None:
            print("EVALUATION STAGE UPDATE RECIEVED")
            EVALUATION_STAGE = request.form.get('evaluation_stage')
            print(EVALUATION_STAGE)
            return redirect(url_for('refresh'))
        else:
            print("EVALUATION STAGE UPDATE NOT RECIEVED")
            error_message = 'Evaluation stage update not recieved. Please restart the process'
            return render_template('error.html', error_message=error_message), 500
    else:
        error_message = 'An error updating stage happened. Please, restart the process.'
        return render_template('error.html', error_message=error_message), 500



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
        global COST_WEIGHT, PERFORMANCE_WEIGHT
        filename = file.filename
        file.save(os.getcwd()+"/temp/"+filename)
        COST_WEIGHT = float(request.form['cost'])
        PERFORMANCE_WEIGHT = float(request.form['performance'])
        cost_and_performance = {'cost_weight': COST_WEIGHT, 'performance_weight' : PERFORMANCE_WEIGHT}
        # Envía el archivo al microservicio
        try:
            url = INFORMATION_PROCESSING_URL+"/start"
            print(cost_and_performance)
            files = {filename: open(os.getcwd()+"/temp/"+filename, 'rb')}
            response = requests.post(url, files=files, data=cost_and_performance)
            if response.status_code == 200:
                # Eliminar archivo temporal
                info_message = "Information was correctly send. The process has started."
                #return render_template('progress.html', info_message=info_message), 200
                return redirect(url_for('refresh'))
            else:
                error_message = 'An error processing the information happened. Please, restart the process.'
                return render_template('error.html', error_message=error_message), 500
        except Exception as e:
            error_message = 'An exception has been launched\n' + e
            return render_template('error.html', error_message=error_message), 500
            
    else:
        logging.debug("REQUEST /upload --> NO ZIP FILE SELECTED")
        error_message = 'The file is not a valiz .zip. Please, restart the process.'
        return render_template('error.html', error_message=error_message), 500

if __name__ == '__main__':
    logging.basicConfig(filename=os.getcwd()+'/web.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    #app.run(host="127.0.0.1", port=8585,debug=True)
    app.run(host="0.0.0.0", port=8585,debug=True)
