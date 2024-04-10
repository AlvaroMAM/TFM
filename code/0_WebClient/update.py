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
from ..config.config import TOPIC_WEB, TOPIC_RESET_PHASES, KAFKA_SERVER_URL, WEB_CLIENT_DEVELOPMENT_URL

if __name__ == "__main__":
    FLOW_STATUS = ['INFORMATION_PROCESSING','MACHINES_CANDIDATES', 'DEPLOYMENT_COMBINATIONS', 'COST-PERFORMANCE', 'UTILITY_CALCULATOR'] # DEPLOYMENT_COMBINATIONS = GENERATOR
    logging.basicConfig(filename='update.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    counter = 0
    consumer = KafkaConsumer([TOPIC_WEB, TOPIC_RESET_PHASES], )
    for message in consumer: # Solo entra si existe un mensaje
        logging.debug("MESSAGE RECIEVED - " + message) 
        logging.debug(message)
        print(message)
        if message.topic == TOPIC_WEB:
            logging.debug("PROCESSING TOPIC - " + message.topic)
            r = requests.put(WEB_CLIENT_DEVELOPMENT_URL+"/update", data={'phase' : FLOW_STATUS[counter]})
            logging.debug("RESPONSE FROM WEB - " + r.text)
            counter = counter + 1
            logging.debug("COUNTER INCREMENTED : " + str(counter))
        else:
            #reset counter --> TOPIC_RESET_PHASES
            logging.debug("PROCESSING TOPIC - " + message.topic)
            counter = 0
            logging.debug("COUNTER RESET : " + str(counter))

    
