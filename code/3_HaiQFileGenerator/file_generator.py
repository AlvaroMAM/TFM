from kafka import KafkaConsumer
from config.config import KAFKA_SERVER_URL, TOPIC_QPU_CANDIDATES, TOPIC_CPU_CANDIDATES, TOPIC_BEHAVIOURAL
import json
import logging
import os

behavioural = None
cpu_candidates = None
qpu_candidates = None

def processing_topics():
    global behavioural, cpu_candidates, qpu_candidates
    # Procesar mensajes de los topics
    for message in consumer:
        topic = message.topic
        if topic == TOPIC_BEHAVIOURAL:
            # Procesando Behavioural File
            file_message = message.value
            with open('received_file', 'w') as f:
                f.write(file_message)
            print(f"Procesado mensaje de archivo desde topic3 y guardado como received_file")
        elif topic == TOPIC_CPU_CANDIDATES:
            # Procesando CPUs
            json1 = message.value
            print(f"Procesado mensaje JSON 1 desde topic1: {json1}")
        elif topic == TOPIC_QPU_CANDIDATES:
            # Procesando QPUs
            json2 = message.value
            print(f"Procesado mensaje JSON 2 desde topic2: {json2}")
        if behavioural != None and cpu_candidates != None and qpu_candidates!=None:
            # Una vez leidas las 3, me salgo
            break

def generating_haiq_file():
    qpu_machines, qpu_services = quantum_generator_string()
    cpu_machines, cpu_services = cpu_generator_string()
    # Concatenar todo
    # file_string = ""
    #   Leer archivo de estilo arquitectónico 
    #   architectural_style_string = Convertirlo a string
    # String (behaviour) DEBE VENIR YA COMO STRING CUANDO SE LEE DE KAFKA
    # concatenar estilo arquitectónico y behaviour
    # file_string = architecturar_style_string + behavioural_string + qpu_machines + cpu_machines + qpu_services + cpu_services
    # Guardar string como archivo .haiq en carpeta ./temp
    return None        
if __name__=='__main__':
    consumer = KafkaConsumer(
    TOPIC_BEHAVIOURAL, TOPIC_CPU_CANDIDATES, TOPIC_QPU_CANDIDATES,
    bootstrap_servers=[KAFKA_SERVER_URL],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    processing_topics()
    generating_haiq_file()