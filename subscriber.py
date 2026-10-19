# sub_dht.py — Classwork Subscriber（由 sub.py 修改）
# 訂閱 iot/dht11，印出收到的「濕度,溫度」
#
# 用法： python sub_dht.py [Broker IP]

import sys

import paho.mqtt.client as mqtt

BROKER_IP = "192.168.43.10"   # ← 改成 Broker 那台電腦的 IP
BROKER_PORT = 1883
TOPIC = "iot/dht11"


def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(getattr(rc, "value", rc)))  # 0 = 成功
    client.subscribe(TOPIC)   # 寫在 on_connect：斷線重連後會自動重新訂閱


def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))


def make_client():
    try:  # paho-mqtt 2.x
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:  # paho-mqtt 1.x
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
