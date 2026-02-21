"""
Serial Gateway - Fog Service
Bridges Arduino USB serial communication with MQTT broker.
- Reads Arduino serial messages, publishes to crosswalk/state and crosswalk/event
- Subscribes to crosswalk/command, forwards START commands to Arduino
"""

import json
import time
import serial
from paho.mqtt import client as mqtt

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883

TOPIC_CMD = "crosswalk/command"
TOPIC_STATE = "crosswalk/state"
TOPIC_EVENT = "crosswalk/event"

# Serial Configuration - UPDATE THIS TO YOUR ARDUINO PORT
# Windows: COM3, COM4, etc. (check Device Manager)
# macOS: /dev/tty.usbmodem* or /dev/tty.usbserial*
# Linux: /dev/ttyUSB0 or /dev/ttyACM0
SERIAL_PORT = "COM7"
BAUD = 115200


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages - forward START command to Arduino."""
    payload = msg.payload.decode("utf-8").strip()
    if payload == "START":
        userdata["ser"].write(b"START\n")
        userdata["ser"].flush()
        print(f"Sent START to Arduino")


def main():
    # Initialize serial connection
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.1)
    time.sleep(2)  # Wait for Arduino to reset

    # Initialize MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.user_data_set({"ser": ser})
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe(TOPIC_CMD)
    client.loop_start()

    print(f"serial_gateway running on {SERIAL_PORT}...")

    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        ts = time.time()

        if line.startswith("STATE="):
            state = line.split("=", 1)[1]
            payload = json.dumps({"state": state, "ts": ts})
            client.publish(TOPIC_STATE, payload)
            print(f"State: {state}")
        elif line.startswith("EVENT="):
            ev = line.split("=", 1)[1]
            payload = json.dumps({"event": ev, "ts": ts})
            client.publish(TOPIC_EVENT, payload)
            print(f"Event: {ev}")
        else:
            payload = json.dumps({"raw": line, "ts": ts})
            client.publish(TOPIC_EVENT, payload)
            print(f"Raw: {line}")


if __name__ == "__main__":
    main()

