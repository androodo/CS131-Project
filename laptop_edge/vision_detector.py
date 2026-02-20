"""
Vision Detector - Edge A (Laptop)
Detects motion from webcam and publishes pedestrian crossing requests via MQTT.
"""

import time
import cv2
import json
from paho.mqtt import client as mqtt

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC_REQ = "crosswalk/request"

# Detection Configuration
COOLDOWN_SEC = 8          # Minimum seconds between requests
MOTION_THRESHOLD = 25000  # Adjust based on your environment
SUSTAIN_FRAMES = 8        # Frames of sustained motion before triggering


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Webcam not found")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    prev_gray = None
    sustain = 0
    last_fire = 0

    print("vision_detector running... press 'q' to quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_gray is None:
            prev_gray = gray
            continue

        delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_score = int(thresh.sum())

        # Simple sustain logic
        if motion_score > MOTION_THRESHOLD:
            sustain += 1
        else:
            sustain = max(0, sustain - 1)

        now = time.time()
        if sustain >= SUSTAIN_FRAMES and (now - last_fire) > COOLDOWN_SEC:
            payload = {
                "source": "vision",
                "event": "pedestrian_request",
                "motion_score": motion_score,
                "ts": now
            }
            client.publish(TOPIC_REQ, json.dumps(payload))
            last_fire = now
            sustain = 0
            print("Published request:", payload)

        # Debug view
        cv2.putText(frame, f"motion={motion_score} sustain={sustain}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("vision", frame)

        prev_gray = gray

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

