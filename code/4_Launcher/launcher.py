from flask import Flask, render_template, request
#import requests
import subprocess
import os
import logging
import requests
from config.config import INFORMATION_PROCESSING_URL_OUT


app = Flask(__name__)


@app.route('/')
def index():
    logging.debug("REQUEST / --> RENDERING TEMPLATE")
    return render_template('home.html')

@app.route('/launch-haiq', methods=['POST'])
def launch_haiq():
    """
    Recieved the file generated by the the Haiq File Generator
    Save the file in the corresponding path
    Launch the program
    """
    recieved_file = None
    path_to_save = "/Users/iquantum/Desktop/HaiQ-project/examples/QuantumClassicalApp/"
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
            """
            #Lanzar run.sh
            script_path = os.path.join(path_to_save,'run.sh')
            try:
                result = subprocess.run(['bash', script_path], cwd=path_to_save, check=True, capture_output=True, text=True)
                output = result.stdout 
                #Añadir al script una salida (Tipo 200 si okey)
                if int(output) == 200:
                    print("SCRIPT EJECUTADO CORRECTAMENTE")
                    logging.debug("HAIQ LAUNCHER --> HAIQ FINISHED CORRECTLY")
                else:
                    print("SE HA PRODUCIDO UN ERROR AL EJECUTAR EL SCRIPT")
                    logging.debug("HAIQ LAUNCHER --> HAIQ FINISHED WRONG")
            except subprocess.CalledProcessError as e:
                print("SE HA PRODUCIDO UNA EXCEPCIÓN AL EJECUTAR EL SCRIPT")
                logging.debug("HAIQ LAUNCHER --> EXCEPTION WHILE HAIQ RUN")
                print(e)
            haiq_result_path = '' #To Complete
            if os.path.exists(haiq_result_path):
                try:
                    # Mandar resultado a INFO PROCESSING
                    url = INFORMATION_PROCESSING_URL+"/haiq-result"
                    files = {"haiq-result": open(os.getcwd()+haiq_result_path, 'rb')}
                    response = requests.post(url, files=files)
                    if response.status_code == 200:
                        print("HAIQ RESULT SUCESSFULLY SENT")
                        logging.debug("HAIQ LAUNCHER --> HAIQ RESULT SUCESSFULLY SENT")
                    else:
                        print("SENDING HAIQ RESULT WAS WRONG")
                        logging.debug("HAIQ LAUNCHER --> SENDING HAIQ RESULT WAS WRONG")
                except Exception as e:
                    print("ERROR AL LEER RESULTADO DE HAIQ")
                    logging.debug("HAIQ LAUNCHER --> EXCEPTION WHILE HAIQ RUN")
                    print(e)
            else:
                print("RESULTADO DE HAIQ NO ENCONTRADO")
            """
        else:
            print("RECIBIDO PERO NO LEIDO CORRECTAMENTE")
            logging.debug("HAIQ LAUNCHER --> File didn't read correctly")
    else:
        logging.debug("HAIQ LAUNCHER --> Something was wrong :(")
        print("NO SE HA RECIBIDO ARCHIVO HAIQ")

if __name__ == '__main__':
    logging.basicConfig(filename=os.getcwd()+'/launcher.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') #CREATING LOGGING CONFIGURATION
    #app.run(host="127.0.0.1", port=8585,debug=True)
    app.run(host="0.0.0.0", port=8888,debug=True)