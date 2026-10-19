# ble_30s.py — Classwork 2（Demo 給助教看）
# Arduino A + DHT11 --藍牙--> Arduino B --USB--> 本程式 --MQTT--> Broker --> sub_dht.py
# 收集 30 秒的 DHT11 資料，每一筆都 publish 到 Broker。
#
# 用法： python ble_30s.py [Arduino B 的序列埠] [Broker IP]
#   例： python ble_30s.py COM6 192.168.43.10

import re
import sys
import time

import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports

SERIAL_PORT = None            # Arduino B 的序列埠，例如 "COM6"；None = 自動偵測
BROKER_IP = "192.168.43.10"   # ← 改成 Broker 那台電腦的 IP
BROKER_PORT = 1883
TOPIC = "iot/dht11"
BAUD = 9600
DURATION = 30                 # 秒

# 支援 Arduino B 轉出的純 CSV，以及帶有 Humidity/Temperature 標籤的輸出。
# 用 findall 可防止兩筆資料黏在同一行時漏掉後面的資料。
RE_CSV = re.compile(r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)")
RE_LABELLED = re.compile(
    r"Humidity:\s*(-?\d+(?:\.\d+)?).*?Temperature:\s*(-?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def parse_records(line):
    """回傳一行中所有 (濕度, 溫度) 記錄。"""
    labelled = RE_LABELLED.findall(line)
    if labelled:
        return labelled
    return RE_CSV.findall(line)


def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = f"{p.description} {p.manufacturer or ''}".lower()
        if any(k in desc for k in ("arduino", "ch340", "ch341", "usb serial", "usb-serial", "acm")):
            return p.device
    if ports:
        return ports[0].device
    sys.exit("找不到序列埠：確認 Arduino B 有插上，或直接指定，例如 python ble_30s.py COM6")


def make_client():
    try:  # paho-mqtt 2.x
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:  # paho-mqtt 1.x
        return mqtt.Client()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else (SERIAL_PORT or find_port())
    broker = sys.argv[2] if len(sys.argv) > 2 else BROKER_IP

    client = make_client()
    client.connect(broker, BROKER_PORT, 60)
    client.loop_start()
    print(f"MQTT 已連線 {broker}:{BROKER_PORT}，topic = {TOPIC}")

    ser = serial.Serial(port, BAUD, timeout=1)
    time.sleep(2)               # 開序列埠會讓 Arduino B 重開機，等它跑完 setup
    ser.reset_input_buffer()

    print(f"從 {port} 收集 {DURATION} 秒藍牙資料...")
    count = 0
    start = time.time()
    try:
        while time.time() - start < DURATION:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            records = parse_records(line)
            if not records:
                print(f"(略過) {line}")
                continue
            for h, t in records:
                payload = f"{float(h):.2f},{float(t):.2f}"
                client.publish(TOPIC, payload)
                count += 1
                print(f"[{time.time() - start:5.1f}s] #{count} {payload}")
    except KeyboardInterrupt:
        print("\n提前停止")
    finally:
        ser.close()
        time.sleep(0.5)         # 讓最後幾筆送完
        client.loop_stop()
        client.disconnect()
    print(f"完成：{DURATION} 秒內共 publish {count} 筆到 {TOPIC}")


if __name__ == "__main__":
    main()
