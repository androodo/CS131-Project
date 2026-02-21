# CS131 Final Project - Smart Crosswalk System

An edge-fog-cloud IoT system for pedestrian crosswalk management using computer vision and Arduino.

## Quick Start

Follow these steps every time you want to run the system.

### One-time setup (do this only once)

**1. Install Python dependencies**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Upload the Arduino sketch**
- Open `arduino/crosswalk_controller/crosswalk_controller.ino` in Arduino IDE
- Plug in your Arduino via USB
- Select your board under **Tools > Board** and your port under **Tools > Port**
- Click **Upload** and wait for "Done uploading"
- Check **Tools > Serial Monitor** (115200 baud) — you should see `STATE=IDLE_GREEN`
- Close the Serial Monitor when done

**3. Set your COM port**
- Open `services/serial_gateway.py` and set `SERIAL_PORT` to match your Arduino's port
- On Windows, check **Device Manager → Ports (COM & LPT)** to find it (e.g. `COM7`)

---

### Running the system (do this every time)

> **Before starting:** Make sure Docker Desktop is running and Arduino IDE's Serial Monitor is closed.

**Step 1 — Start the MQTT broker** (in the `fog/` folder)
```powershell
cd fog
docker compose up -d
cd ..
```

**Step 2 — Start the Serial Gateway** (Terminal 1)
```powershell
.\.venv\Scripts\Activate.ps1
python services/serial_gateway.py
```
You should see: `serial_gateway running on COMx...`

**Step 3 — Start the Rules Engine** (Terminal 2)
```powershell
.\.venv\Scripts\Activate.ps1
python services/rules_engine.py
```
You should see: `rules_engine running...`

**Step 4 — Start the Vision Detector** (Terminal 3)
```powershell
.\.venv\Scripts\Activate.ps1
python laptop_edge/vision_detector.py
```
A webcam window should open showing your camera feed.

**Step 5 — Test it**
- Wave or walk in front of the webcam → the LEDs should cycle: **Green → Yellow → Red + Walk → Green**
- Or press the button on the Arduino to trigger the cycle manually

---

## Architecture

```
┌─────────────────┐      ┌─────────────────────────────────────┐      ┌──────────────┐
│   Edge A        │      │           Fog Layer                 │      │    Cloud     │
│   (Laptop)      │      │         (Laptop Services)           │      │              │
│                 │      │                                     │      │              │
│  ┌───────────┐  │      │  ┌─────────────┐  ┌──────────────┐  │      │  ┌────────┐  │
│  │  Webcam   │──┼──────┼─▶│ Rules Engine│─▶│Serial Gateway│──┼──────┼─▶│Adafruit│  │
│  │  Motion   │  │ MQTT │  └─────────────┘  └──────────────┘  │      │  │   IO   │  │
│  │ Detection │  │      │        │                │           │      │  └────────┘  │
│  └───────────┘  │      │        ▼                ▼           │      │              │
│                 │      │  ┌─────────────────────────────┐    │      │              │
│                 │      │  │    MQTT Broker (Mosquitto)  │    │      │              │
│                 │      │  └─────────────────────────────┘    │      │              │
└─────────────────┘      └─────────────────────────────────────┘      └──────────────┘
                                          │
                                          ▼
                               ┌─────────────────┐
                               │     Edge B      │
                               │   (Arduino)     │
                               │                 │
                               │  Traffic Light  │
                               │  State Machine  │
                               └─────────────────┘
```

## Components

- **Edge A (Vision Detector)**: Laptop webcam detects pedestrian motion and publishes crossing requests
- **Edge B (Arduino)**: Traffic light LED state machine, responds to START commands
- **Fog Layer**: MQTT broker + Rules Engine + Serial Gateway on laptop
- **Cloud**: Event logging to Adafruit IO

## Hardware Requirements

### Arduino Setup
- Arduino board (Uno, Nano, or Mega)
- 4 LEDs: Red, Yellow, Green (traffic), Walk (pedestrian)
- 4 resistors (220Ω or 330Ω)
- 1 push button (optional, for manual requests)
- Breadboard + jumper wires

### Pin Mapping
| Component | Arduino Pin |
|-----------|-------------|
| Red LED   | D2          |
| Yellow LED| D3          |
| Green LED | D4          |
| Walk LED  | D5          |
| Button    | D6          |

### Wiring
- Each LED: Arduino pin → resistor → LED (+) → LED (-) → GND
- Button: One side to D6, other side to GND (using INPUT_PULLUP)

## Software Requirements

- Python 3.10+
- Docker Desktop
- Arduino IDE 2.x
- Git

## Installation

### 1. Clone the repository
```powershell
git clone https://github.com/androodo/CS131-Project.git
cd CS131-Project
```

### 2. Create Python virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Start MQTT broker
```powershell
cd fog
docker compose up -d
cd ..
```

### 4. Upload Arduino sketch
1. Open `arduino/crosswalk_controller.ino` in Arduino IDE
2. Select your board and port
3. Click Upload
4. Verify in Serial Monitor (115200 baud) that you see `STATE=IDLE_GREEN`

### 5. Configure Serial Port
Edit `services/serial_gateway.py` and update `SERIAL_PORT` to match your Arduino:
- Windows: `COM3`, `COM4`, etc. (check Device Manager → Ports)
- macOS: `/dev/tty.usbmodem*` or `/dev/tty.usbserial*`
- Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`

## Running the System

**Important**: Close Arduino Serial Monitor before running the gateway!

Run each service in a separate terminal:

### Terminal 1: Serial Gateway
```powershell
.\.venv\Scripts\Activate.ps1
python services/serial_gateway.py
```

### Terminal 2: Rules Engine
```powershell
.\.venv\Scripts\Activate.ps1
python services/rules_engine.py
```

### Terminal 3: Cloud Logger (optional)
```powershell
.\.venv\Scripts\Activate.ps1
$env:AIO_USER="your_adafruit_username"
$env:AIO_KEY="your_adafruit_key"
python services/cloud_logger.py
```

### Terminal 4: Vision Detector
```powershell
.\.venv\Scripts\Activate.ps1
python laptop_edge/vision_detector.py
```

## Testing

1. Wave your hand in front of the webcam
2. After sustained motion, a crossing request should be published
3. Rules engine sends START command to Arduino
4. Arduino cycles through: GREEN → YELLOW → RED → WALK → GREEN

### Manual Testing
Press the button on the Arduino to trigger a crossing cycle manually.

## Troubleshooting

### MQTT Issues
```powershell
# Check if broker is running
docker ps

# Check broker logs
docker logs mosquitto
```

### Serial Issues
- Only one program can use the serial port - close Arduino Serial Monitor
- Verify correct COM port in Device Manager
- Try unplugging and replugging the Arduino

### Vision Detector Issues
- Adjust `MOTION_THRESHOLD` if too sensitive or not sensitive enough
- Adjust `SUSTAIN_FRAMES` for faster/slower triggering
- Keep consistent lighting, avoid pointing at windows

## Project Structure

```
crosswalk-edge/
├── arduino/
│   └── crosswalk_controller.ino    # Arduino traffic light state machine
├── fog/
│   ├── docker-compose.yml          # MQTT broker container
│   └── mosquitto.conf              # Broker configuration
├── laptop_edge/
│   └── vision_detector.py          # Webcam motion detection
├── services/
│   ├── serial_gateway.py           # USB serial ↔ MQTT bridge
│   ├── rules_engine.py             # Fog coordinator logic
│   └── cloud_logger.py             # Adafruit IO logging
├── requirements.txt
└── README.md
```

## MQTT Topics

| Topic | Description |
|-------|-------------|
| `crosswalk/request` | Vision detector publishes pedestrian requests |
| `crosswalk/command` | Rules engine publishes START commands |
| `crosswalk/state`   | Arduino state changes (via serial gateway) |
| `crosswalk/event`   | Button presses and other events |

## Technologies Used

- **Arduino IDE** - Microcontroller programming
- **Docker Desktop** - Container runtime
- **Eclipse Mosquitto** - MQTT broker
- **Python 3** + venv - Application runtime
- **paho-mqtt** - MQTT client library
- **pyserial** - Serial communication
- **opencv-python** - Computer vision
- **requests** - HTTP client for cloud logging
- **Adafruit IO** - Cloud event logging platform

