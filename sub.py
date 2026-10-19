# sub.py（修正版）— 訂閱 hello/world
# 用法： python sub.py <BROKER_IP>
import sys

import paho.mqtt.client as mqtt

BROKER_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.43.10"


def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(getattr(rc, "value", rc)))  # 0 = 成功
    client.subscribe("hello/world")   # 是 subscribe，不是投影片寫的 subscriber


def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))


try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883)
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
