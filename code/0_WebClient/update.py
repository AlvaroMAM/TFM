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
import time

if __name__ == "__main__":
    logging.basicConfig(filename=os.getcwd()+'/update.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    #consumer_topics = [TOPIC_WEB, TOPIC_RESET_PHASES]
   
    consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    consumer.subscribe([TOPIC_WEB])
    print("Consumer launched")
    logging.debug("UPDATE - CONSUMER LAUNCHED")
    for message in consumer: # Solo entra si existe un mensaje
        current_phase = message.value
        logging.debug("MESSAGE RECIEVED - " + current_phase) 
        print(current_phase)
        if message.topic == TOPIC_WEB:
            logging.debug("PROCESSING TOPIC - " + message.topic)
            requests.post(WEB_CLIENT_DEVELOPMENT_URL+"/refresh", data={'evaluation_stage' : current_phase})
            logging.debug("CURRENT PHASE : " + current_phase)
            time.sleep(2)

    
