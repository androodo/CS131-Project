"""
Cloud Logger - Fog Service
Logs all MQTT events to the cloud (Adafruit IO).
Set environment variables before running:
  - AIO_USER: Your Adafruit IO username
  - AIO_KEY: Your Adafruit IO API key
  - AIO_FEED: Feed name (default: crosswalk_events)
"""

import os
import time
import json
import requests
from paho.mqtt import client as mqtt

# Adafruit IO Configuration (set via environment variables)
AIO_USER = os.getenv("AIO_USER")
AIO_KEY = os.getenv("AIO_KEY")
FEED = os.getenv("AIO_FEED", "crosswalk_events")

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPICS = ["crosswalk/request", "crosswalk/event", "crosswalk/state"]


def post_to_adafruit(value: str):
    """Post a data point to Adafruit IO feed."""
    if not AIO_USER or not AIO_KEY:
        return
    
    url = f"https://io.adafruit.com/api/v2/{AIO_USER}/feeds/{FEED}/data"
    headers = {"X-AIO-Key": AIO_KEY}
    try:
        requests.post(url, headers=headers, json={"value": value}, timeout=5)
    except Exception as e:
        print(f"Failed to post to Adafruit IO: {e}")


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and log to cloud."""
    data = {
        "topic": msg.topic,
        "payload": msg.payload.decode("utf-8"),
        "ts": time.time()
    }
    line = json.dumps(data)
    print(f"CLOUD LOG: {line}")
    
    if AIO_USER and AIO_KEY:
        post_to_adafruit(line)


def main():
    if not AIO_USER or not AIO_KEY:
        print("WARNING: AIO_USER and AIO_KEY not set. Running in local-only mode.")
        print("Set environment variables to enable Adafruit IO logging:")
        print("  $env:AIO_USER='your_username'")
        print("  $env:AIO_KEY='your_key'")
        print()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    
    for t in TOPICS:
        client.subscribe(t)
    
    print("cloud_logger running...")
    client.loop_forever()


if __name__ == "__main__":
    main()

