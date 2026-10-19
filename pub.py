# pub.py（修正版）— 每 5 秒 publish "NTNU" 到 hello/world
# 用法： python pub.py <BROKER_IP>
import sys
import time

import paho.mqtt.client as mqtt

BROKER_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.43.10"

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

client.connect(BROKER_IP, port=1883)
client.loop_start()

try:
    while True:
        client.publish("hello/world", "NTNU")
        print("published hello/world NTNU")
        time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
