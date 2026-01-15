import json
import time
import requests
import paho.mqtt.client as mqtt

MQTT_HOST = "[ip address da Gateway]"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/#"

MQTT_USER = None
MQTT_PASSWORD = None

LOGSTASH_URL = "http://localhost:5044"
LOGSTASH_USER = "elastic"
LOGSTASH_PASSWORD = "changeme"

session = requests.Session()
session.auth = (LOGSTASH_USER, LOGSTASH_PASSWORD)
session.headers.update({"Content-Type": "application/json"})


def send_to_logstash(event: dict):
    for _ in range(3):
        try:
            r = session.post(LOGSTASH_URL, data=json.dumps(event), timeout=5)
            if r.status_code in (200, 201, 202):
                return True
            print(f"[LOGSTASH] HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[LOGSTASH] erro a enviar: {e}")
        time.sleep(1)
    return False


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] ligado ao broker {MQTT_HOST}:{MQTT_PORT} (rc={reason_code})")
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] subscrito: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload_raw = msg.payload.decode("utf-8", errors="replace").strip()
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        payload = {"value": payload_raw}
    device = None
    if topic.startswith("zigbee2mqtt/"):
        parts = topic.split("/", 1)
        device = parts[1] if len(parts) > 1 else None

    event = {
        "source": "zigbee2mqtt",
        "topic": topic,
        "device": device,
        "payload": payload,
        "ingested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    ok = send_to_logstash(event)
    if ok:
        print(f"[OK] {topic}")
    else:
        print(f"[FALHA] {topic}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
