"""
Rules Engine - Fog Service (Coordinator Logic)
Subscribes to pedestrian requests and button events.
If not in a crossing cycle, publishes START command to trigger Arduino.
"""

import time
import json
from paho.mqtt import client as mqtt

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883

TOPIC_REQ = "crosswalk/request"
TOPIC_EVENT = "crosswalk/event"
TOPIC_STATE = "crosswalk/state"
TOPIC_CMD = "crosswalk/command"

# Cooldown to prevent rapid re-triggering
COOLDOWN_SEC = 6

# Global state tracking
state = "UNKNOWN"
busy_until = 0


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and apply rules logic."""
    global state, busy_until

    t = msg.topic
    payload = msg.payload.decode("utf-8").strip()
    now = time.time()

    # Update state if we receive a state message
    if t == TOPIC_STATE:
        try:
            data = json.loads(payload)
            state = data.get("state", state)
            print(f"State updated: {state}")
        except:
            pass

    # Handle requests and events
    if t in [TOPIC_REQ, TOPIC_EVENT]:
        # Check if we're in cooldown period
        if now < busy_until:
            print(f"In cooldown, ignoring request (wait {busy_until - now:.1f}s)")
            return

        # Start a crossing cycle
        client.publish(TOPIC_CMD, "START")
        busy_until = now + COOLDOWN_SEC
        print(f"RULES: sent START, next allowed after {COOLDOWN_SEC}s cooldown")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    client.subscribe(TOPIC_REQ)
    client.subscribe(TOPIC_EVENT)
    client.subscribe(TOPIC_STATE)

    print("rules_engine running...")
    client.loop_forever()


if __name__ == "__main__":
    main()

