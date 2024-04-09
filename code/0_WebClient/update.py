"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Proceso encargado de mandar solicitud de actualización del estado a la web
"""

from threading import Thread, Lock
import logging
import requests
from kafka import KafkaConsumer
from ..topics.topics import TOPIC_WEB, TOPIC_RESET_PHASES


def updating_web(lock):
    global counter
    consumer = KafkaConsumer(TOPIC_WEB)
    for message in consumer: # Solo entra si existe un mensaje
        lock.acquire()
        logging.debug("UPDATING COUNTER - ACQUIRE LOCK") 
        logging.debug(message)
        print(message)
        r = requests.put(WEB_DEVELOPMENT_URL+"/update", data={'phase' : FLOW_STATUS[cont]})
        logging.debug(r.text)
        counter = counter + 1
        logging.debug("INCREMENT COUNTER, VALUE:" + str(counter))
        lock.release()
        logging.debug("UPDATING COUNTER - RELEASE LOCK")

def reset_counter(lock):
    global counter
    consumer = KafkaConsumer(TOPIC_RESET_PHASES)
    for message in consumer: # Solo entra si existe un mensaje
        lock.acquire()
        logging.debug("RESET COUNTER - ACQUIRE LOCK") 
        logging.debug(message)
        print(message)
        counter = 0
        logging.debug("RESET COUNTER, VALUE:" + str(counter))
        lock.release()
        logging.debug("RESET COUNTER - RELEASE LOCK")


if __name__ == "__main__":
    FLOW_STATUS = ['INFORMATION_PROCESSING','MACHINES_CANDIDATES', 'DEPLOYMENT_COMBINATIONS', 'COST-PERFORMANCE', 'UTILITY_CALCULATOR'] # DEPLOYMENT_COMBINATIONS = GENERATOR
    # WEB_PRODUCTION_URL = ""
    WEB_DEVELOPMENT_URL = "http://127.0.0.1:8585"
    logging.basicConfig(filename='update.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    counter = 0
    #LAUNCHING THREADS
    lock = Lock()
    update_web_task = Thread(updating_web, args=(lock,))
    reset_counter_task = Thread(reset_counter, args=(lock,))
    update_web_task.start()
    reset_counter_task.start()
    update_web_task.join()
    reset_counter_task.join()
    
