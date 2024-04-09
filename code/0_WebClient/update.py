import logging
import requests
from kafka import KafkaConsumer
from ..topics.topics import TOPIC_WEB, TOPIC_RESET_PHASES


def updating_web():
    consumer = KafkaConsumer(TOPIC_WEB)
    for message in consumer: # Solo entra si existe un mensaje
        #lock counter
        logging.debug(message)
        print(message)
        r = requests.put(WEB_DEVELOPMENT_URL+"/update", data={'phase' : FLOW_STATUS[cont]})
        logging.debug(r.text)
        counter = counter + 1
        #release counter
        logging.debug("INCREMENT COUNTER, VALUE:" + str(counter))

def reset_counter(c):
    consumer = KafkaConsumer(TOPIC_RESET_PHASES)
    for message in consumer: # Solo entra si existe un mensaje
        #lock counter
        logging.debug(message)
        print(message)
        counter = 0
        #release counter
        logging.debug("RESET COUNTER, VALUE:" + str(counter))


if __name__ == "__main__":
    FLOW_STATUS = ['INFORMATION_PROCESSING','MACHINES_CANDIDATES', 'DEPLOYMENT_COMBINATIONS', 'COST-PERFORMANCE', 'UTILITY_CALCULATOR'] # DEPLOYMENT_COMBINATIONS = GENERATOR
    #WEB_PRODUCTION_URL
    WEB_DEVELOPMENT_URL = "http://127.0.0.1:8585"
    logging.basicConfig(filename='update.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    counter = 0
    #LAUNCH THREADS
    updating_web(counter)
    reset_counter(counter)
