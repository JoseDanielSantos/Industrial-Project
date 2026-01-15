import logging
import sys
import json
import time
import paho.mqtt.client as mqtt
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.transport import HttpTransport

LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5044
LOGSTASH_USER = "elastic" 
LOGSTASH_PASSWORD = "changeme"

MQTT_BROKER = "192.168.50.2"
MQTT_TOPIC = "sensores/#" # O cardinal ouve TUDO o que vier de sensores

def setup_logger():
    logger = logging.getLogger("sensor-logstash")
    logger.setLevel(logging.INFO)
    if logger.handlers: return logger

    transport = HttpTransport(
        host=LOGSTASH_HOST, port=LOGSTASH_PORT, timeout=5.0,
        username=LOGSTASH_USER, password=LOGSTASH_PASSWORD
    )
    handler = AsynchronousLogstashHandler(
        host=LOGSTASH_HOST, port=LOGSTASH_PORT, transport=transport, database_path=None
    )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Ligado ao MQTT Broker. A subscrever...")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Erro na ligação MQTT: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Recebido: {payload}")
        
        # Tenta converter JSON, senão envia como texto cru
        try:
            data = json.loads(payload)
        except:
            data = {"message": payload}
            
        logger = logging.getLogger("sensor-logstash")
        logger.info("iot_event", extra=data)
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    # Pequena espera inicial para garantir que a rede está pronta
    time.sleep(5) 
    logger = setup_logger()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_forever() # Mantém o script vivo para sempre
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)
