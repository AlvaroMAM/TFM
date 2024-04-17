"""
Alumno: Álvaro Manuel Aparicio Morales
Tutores: Javier Cámara y Jose Garcia-Alonso
Máster Universitario en Ingeniería Informátcia
Universidad de Málaga
Descripcion:
Proceso encargado de mandar solicitud de actualización del estado a la web
"""

from threading import Thread, Lock
from kafka import KafkaConsumer
from config.config import TOPIC_WEB, TOPIC_RESET_PHASES, KAFKA_SERVER_URL, WEB_CLIENT_DEVELOPMENT_URL
import logging
import requests
import json
import os

if __name__ == "__main__":
    FLOW_STATUS = ['INFORMATION_PROCESSING','MACHINES_CANDIDATES', 'DEPLOYMENT_COMBINATIONS', 'COST-PERFORMANCE', 'UTILITY_CALCULATOR'] # DEPLOYMENT_COMBINATIONS = GENERATOR
    logging.basicConfig(filename=os.getcwd()+'/update.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    counter = 0
    consumer_topics = [TOPIC_WEB, TOPIC_RESET_PHASES]
   
    consumer = KafkaConsumer(*consumer_topics, bootstrap_servers=[KAFKA_SERVER_URL])
    print("Consumer launched")
    logging.debug("UPDATE - CONSUMER LAUNCHED")
    for message in consumer: # Solo entra si existe un mensaje
        decoded_message = json.loads(message.value.decode('utf-8'))
        logging.debug("MESSAGE RECIEVED - " + decoded_message) 
        logging.debug(decoded_message)
        print(decoded_message)
        if decoded_message.topic == TOPIC_WEB:
            logging.debug("PROCESSING TOPIC - " + decoded_message.topic)
            #r = requests.put(WEB_CLIENT_DEVELOPMENT_URL+"/update", data={'phase' : FLOW_STATUS[counter]})
            #logging.debug("RESPONSE FROM WEB - " + r.text)
            counter = counter + 1
            logging.debug("COUNTER INCREMENTED : " + str(counter))
        else:
            #reset counter --> TOPIC_RESET_PHASES
            logging.debug("PROCESSING TOPIC - " + decoded_message.topic)
            counter = 0
            logging.debug("COUNTER RESET : " + str(counter))

    
