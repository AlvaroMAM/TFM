from flask import Flask, render_template, request, Response, send_from_directory, abort
#import requests
import subprocess
import os
import logging
import requests
import json
from config.config import INFORMATION_PROCESSING_URL_OUT, KAFKA_SERVER_URL_OUT, TOPIC_WEB


app = Flask(__name__)


@app.route('/')
def index():
    logging.debug("REQUEST / --> RENDERING TEMPLATE")
    return render_template('home.html')

@app.route('/downloadsol', methods=['GET'])
def downloadsol():
    print("DOWNLOAD REQUEST ACHIEVED")
    logging.debug("HAIQ LAUNCHER --> DOWNLOAD REQUEST ACHIEVED")
    solution_name = request.args.get('value')  # El valor enviado en la solicitud GET
    solutions_path = "/Users/iquantum/Desktop/HaiQ-project/results/tasconfigs/" #ACTUALIZAR CUANDO SEPA RUTA REAL
    if not solution_name:
        print("SOLUTION NAME NOT PROVIDED")
        logging.debug("HAIQ LAUNCHER --> SOLUTION NAME NOT PROVIDED")
        abort(400, description="VALUE PARAMETER NOT PROVIDED")
    else:
        print("SOLUTION NAME PROVIDED")
        logging.debug("HAIQ LAUNCHER --> SOLUTION NAME PROVIDED")
        sol_path = os.path.join(solutions_path, f"{solution_name}.json")
        print(sol_path)
        if not os.path.isfile(sol_path):
            print("FILE NOT FOUND")
            logging.debug("HAIQ LAUNCHER --> FILE NOT FOUND")
            abort(404, description="FILE NOT FOUND")
        else:
            # Enviar el archivo para su descarga
            print("FILE FOUND")
            logging.debug("HAIQ LAUNCHER --> FILE FOUND")
            return send_from_directory(solutions_path, f"{solution_name}.json", as_attachment=True)

@app.route('/launch-haiq', methods=['POST'])
def launch_haiq():
    """
    Recieved the file generated by the the Haiq File Generator
    Save the file in the corresponding path
    Launch the program
    """
    # Se guarda 
    recieved_file = None
    #path_to_save = "/Users/iquantum/Desktop/HaiQ-project/examples/QuantumClassicalApp/" El bueno
    path_to_save = "/Users/iquantum/Desktop/HaiQ-project/examples/tas/"
    logging.debug("HAIQ LAUNCHER --> /launch-haiq")
    if request.files:
        logging.debug("HAIQ LAUNCHER --> File recieved")
        # Revisar nombre de ['haiqFile']
        recieved_file = request.files['haiqFile']
        if recieved_file != None:
            print("ARCHIVO RECIBIDO Y LEIDO CORRECTAMENTE")
            logging.debug("HAIQ LAUNCHER --> File read correctly")
            if not os.path.exists(path_to_save):
                print("PATH NO EXISTE")
                try:
                    print("PATH A CREAR")
                    os.makedirs(path_to_save)
                    #Create the run.sh
                    print("QUANTUMCLASSICAL APP FOLDER CREATED FROM SCRATCH") 
                except Exception as e:
                    print("Excepcion")
                    print(e)
            #Saving file
            file_name = "model.haiq"
            print("PROCEDO A GUARDAR")
            recieved_file.save(os.path.join(path_to_save, file_name)) #Tomar la ruta de donde los ejemplos
            print("ARCHIVO GUARDADO")
            logging.debug("HAIQ LAUNCHER --> File saved correctly")
            #Lanzar run.sh
            script_path = os.path.join(path_to_save,'run.sh')
            try:
                print("ARCHIVO GUARDADO")
                result = subprocess.run(['bash', script_path], cwd=path_to_save, check=True, capture_output=True, text=True)
                output = result.stdout
                last_line = output.strip().splitlines()[-1]
                print("SE HA EJECUTADO")
                print(last_line)
                
                #Añadir al script una salida (Tipo 200 si okey)
                if int(last_line) == 200:
                    print("SCRIPT EJECUTADO CORRECTAMENTE")
                    logging.debug("HAIQ LAUNCHER --> HAIQ FINISHED CORRECTLY")
                else:
                    print("SE HA PRODUCIDO UN ERROR AL EJECUTAR EL SCRIPT")
                    logging.debug("HAIQ LAUNCHER --> HAIQ FINISHED WRONG")
            except subprocess.CalledProcessError as e:
                print("SE HA PRODUCIDO UNA EXCEPCIÓN AL EJECUTAR EL SCRIPT")
                logging.debug("HAIQ LAUNCHER --> EXCEPTION WHILE HAIQ RUN")
                print(e)
                return Response("EXCEPTION", status=500, mimetype='text/plain')
            
            haiq_result_path = "/Users/iquantum/Desktop/HaiQ-project/results/" #To Complete
            #haiq_result_path = '' #To Complete 
            if os.path.exists(haiq_result_path):
                try:
                    # Mandar resultado a INFO PROCESSING 
                    # MODIFICAR POR NOMBRE DE ARCHIVO REAL
                    result_file = os.path.join(haiq_result_path,'tasdata.json') 
                    url = INFORMATION_PROCESSING_URL_OUT+"/haiq-result"
                    files = {"haiq-result": open(result_file, 'rb')}
                    response = requests.post(url, files=files)
                    if response.status_code == 200:
                        print("HAIQ RESULT SUCESSFULLY SENT")
                        logging.debug("HAIQ LAUNCHER --> HAIQ RESULT SUCESSFULLY SENT")
                        return Response("HAIQ RESULT SUCESSFULLY SENT", status=200, mimetype='text/plain')
                    else:
                        print("ERROR WHILE SENDING HAIQ RESULT")
                        logging.debug("HAIQ LAUNCHER --> ERROR WHILE SENDING HAIQ RESULT")
                        return Response("ERROR WHILE SENDING HAIQ RESULT", status=500, mimetype='text/plain')
                except Exception as e:
                    print("EXCEPTION WHILE READING HAIQ RESULT FILE")
                    logging.debug("HAIQ LAUNCHER --> EXCEPTION WHILE READING HAIQ RESULT FILE")
                    print(e)
                    return Response("EXCEPTION WHILE READING HAIQ RESULT FILE", status=500, mimetype='text/plain')
            else:
                print("HAIQ RESULT FILE NOT FOUND")
        else:
            print("HAIQ FILE RECIEVED BUT NOT READ")
            logging.debug("HAIQ LAUNCHER --> HAIQ FILE RECIEVED BUT NOT READ")
    else:
        logging.debug("HAIQ LAUNCHER --> HAIQ FILE MISSING")
        print("HAIQ FILE MISSING")

if __name__ == '__main__':
    logging.basicConfig(filename=os.getcwd()+'/launcher.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    #app.run(host="127.0.0.1", port=8585,debug=True)
    app.run(host="0.0.0.0", port=8888,debug=True)