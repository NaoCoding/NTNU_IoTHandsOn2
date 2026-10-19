import re
import sys
import time

import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports

SERIAL_PORT = None
BROKER_IP = "192.168.43.10"
BROKER_PORT = 1883
TOPIC = "iot/dht11"
BAUD = 9600

RE_TESTER = re.compile(r"Humidity:\s*([-\d.]+).*?Temperature:\s*([-\d.]+)")
RE_CSV = re.compile(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)")

def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = f"{p.description} {p.manufacturer or ''}".lower()
        if any(k in desc for k in ("arduino", "ch340", "ch341", "usb serial", "usb-serial", "acm")):
            return p.device
    if ports:
        return ports[0].device
    sys.exit("找不到序列埠：確認 Arduino 有插上，或直接指定，例如 python bridge.py COM5")

def parse(line):
    m = RE_TESTER.search(line) or RE_CSV.search(line)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))

def make_client():
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        return mqtt.Client()

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else (SERIAL_PORT or find_port())
    broker = sys.argv[2] if len(sys.argv) > 2 else BROKER_IP

    client = make_client()
    client.connect(broker, BROKER_PORT, 60)
    client.loop_start()
    print(f"MQTT 已連線 {broker}:{BROKER_PORT}，topic = {TOPIC}")

    ser = serial.Serial(port, BAUD, timeout=3)
    time.sleep(2)
    ser.reset_input_buffer()
    print(f"讀取序列埠 {port} @ {BAUD}（Ctrl+C 停止）")

    try:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            data = parse(line)
            if data is None:
                print(f"(略過) {line}")
                continue
            h, t = data
            payload = f"{h:.2f},{t:.2f}"
            client.publish(TOPIC, payload)
            print(payload)
    except KeyboardInterrupt:
        print("\n停止")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
