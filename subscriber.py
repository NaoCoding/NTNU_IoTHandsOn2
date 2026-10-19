import sys

import paho.mqtt.client as mqtt

BROKER_IP = "192.168.43.10"
BROKER_PORT = 1883
TOPIC = "iot/dht11"

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(getattr(rc, "value", rc)))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))

def make_client():
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        return mqtt.Client()

broker = sys.argv[1] if len(sys.argv) > 1 else BROKER_IP
client = make_client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, BROKER_PORT, 60)
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n停止")
