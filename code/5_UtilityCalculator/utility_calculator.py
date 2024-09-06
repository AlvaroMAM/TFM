from kafka import KafkaConsumer, KafkaProducer
from config.config import KAFKA_SERVER_URL, TOPIC_UTILITY_VALUES, TOPIC_HAIQ_RESULT, WEB_CLIENT_DEVELOPMENT_URL, TOPIC_WEB
import json
import logging
import requests
import base64
import os

HAIQ_RESULTS = None
UTILITY_VALUES_RECIEVED = None

def read_haiq_result():
    results_readed = None
    haiq_result_file = "./temp/results.json"
    with open(haiq_result_file, 'r') as f:
                results_readed = json.load(f)
    return results_readed


def isEmpty(l):
    empty = True
    if len(l) > 0:
        empty = False
    return empty

def insert_sorted_tuple_list(l,t):
    position_to_insert = -1
    if isEmpty(l):
        position_to_insert = 0
    else:
        # Elements in list, must to calculate where to put the new tuple
        for i in range(len(l)):
            if t[1] > l[i][1]:
                position_to_insert = i
                break
    #Insert new element
    if position_to_insert >= 0:
        l.insert(position_to_insert,t)
        return l
        # Eliminando esa comprobación serviría para tener una lista completa de los valores de utilidad
        #if len(l)>3:
        #    return l[:-1]
        #else:
        #    return l
    else:
        return l

def utility_calculation(utility_values):
    #Select the top 3 solutions that have the biggest value after applying the utility theory
    print("UTILITY CALCULATION STARTED")
    print("UTILITY VALUES and TYPE")
    print(utility_values)
    print(type(utility_values))
    utility_tuple_sorted_list = []
    cost_weight = float(utility_values[0])
    performance_weight = float(utility_values[1])
    print(cost_weight)
    print(performance_weight)
    haiq_results = read_haiq_result()
    print(haiq_results)
    for elem in haiq_results:
        print(elem)
        for sol, metrics in elem.items():
            utility_tuple = None
            sol_utility_value = 0
            for metric in metrics:
                for k,v in metric.items():
                    key_utility_value = None
                    if k == 'cost':
                        key_utility_value = cost_weight*float(v)
                    elif k == 'reliability': # Change for performance
                        key_utility_value = performance_weight*float(v)
                    else:
                        key_utility_value = 0
                sol_utility_value = sol_utility_value + key_utility_value
            utility_tuple = (sol, sol_utility_value, metrics)
        #print("BEFORE INSERT INTO SORTED TUPLE LIST",utility_tuple_sorted_list)
        utility_tuple_sorted_list = insert_sorted_tuple_list(utility_tuple_sorted_list,utility_tuple) # Comprobar que se modifica la lista correctamente
        #print("AFTER INSERT INTO SORTED TUPLE LIST", utility_tuple_sorted_list)
    print("UTILITY VALUES CALCULATED")
    #top3_values = utility_tuple_sorted_list[:3]
    print("PREPARING REQUEST")
    logging.debug("UTILITY-CALCULATOR : PREPARING FOR SEND NEW RANKING")  
    #data = json.dumps(top3_values)
    #Probar a enviar todas las soluciones
    data = json.dumps(utility_tuple_sorted_list)
    header = {
        "Content-Type": "application/json"
        }
    response = requests.post(WEB_CLIENT_DEVELOPMENT_URL+'/showResults',headers=header, data=data)
    if response.status_code == 200:
        utility_tuple_sorted_list = []
        print("REQUEST PROCESSED CORRECTLY")
        producer.send(TOPIC_WEB, "FINISHED")
        producer.flush()
        logging.debug("UTILITY-CALCULATOR : REQUEST SUCCESSFULLY PROCESSED")
    else:
        utility_tuple_sorted_list = []
        print("REQUEST WAS NOT PROCESSED")
        logging.debug("UTILITY-CALCULATOR : REQUEST WAS NOT PROCESSED")
        print(response)
        

def processing_topics():
    print("WAITING FOR TOPICS")
    global HAIQ_RESULTS, UTILITY_VALUES_RECIEVED
    # Procesar mensajes de los topics
    logging.debug("UTILITY-CALCULATOR : WAITING FOR MESSAGES")
    for message in consumer:
        logging.debug("UTILITY-CALCULATOR : MESSAGE RECIEVED")
        topic = message.topic
        if topic == TOPIC_HAIQ_RESULT:
            # RECIEVING HAIQ RESULT
            logging.debug("UTILITY-CALCULATOR : MESSAGE FROM TOPIC BEHAVIOURAL")
            haiq_b64 = message.value
            HAIQ_RESULTS = base64.b64decode(haiq_b64)
            with open('./temp/results.json', 'wb') as f:
                f.write(HAIQ_RESULTS)
            logging.debug("UTILITY-CALCULATOR : HAIQ_RESULTS SAVED")
        elif topic == TOPIC_UTILITY_VALUES:
            # RECIEVING UTILITY VALUES (DUPLE) (x,y) (cost, performance)
            logging.debug("UTILITY-CALCULATOR : UTILITY VALUES RECIEVED")
            print(f"PROCESSING MESSAGE FROM TOPIC: {topic}")
            # the values must be a Duple
            UTILITY_VALUES_RECIEVED = json.loads(message.value)
            print("UTILITY VALUES RECIEVED")
            print(UTILITY_VALUES_RECIEVED)
            producer.send(TOPIC_WEB, "UTILITY_CALCULATOR")
            producer.flush()
            utility_calculation(UTILITY_VALUES_RECIEVED)
            HAIQ_RESULTS = None
            logging.debug("UTILITY-CALCULATOR : NEW RANKING GENERATED")   


if __name__=='__main__':
    print("UTILITY CALCULATOR ON")
    logging.basicConfig(filename='utility-calculator.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # CREATING LOGGING CONFIGURATION
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_URL], value_serializer=lambda x: json.dumps(x).encode('utf-8')) # CREATING KAFKA PRODUCER
    consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logging.debug("FILE-GENERATOR : INITIALIZED")
    consumer.subscribe([TOPIC_UTILITY_VALUES, TOPIC_HAIQ_RESULT])
    processing_topics()
    