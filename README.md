<p align="center">
  <img src="https://img.shields.io/badge/Luna-AI%20Plant%20Care-3fb950?style=for-the-badge&logo=leaf&logoColor=white">
  <img src="https://img.shields.io/badge/ESP32-WROOM--32D-blue?style=for-the-badge&logo=espressif&logoColor=white">
  <img src="https://img.shields.io/badge/Gemini-AI-orange?style=for-the-badge&logo=google&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3.11%2B-yellow?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Status-Active-3fb950?style=for-the-badge">
</p>

<h1 align="center">🌱 Luna — Autonomous AI Plant Care System</h1>

<p align="center">
  <em>
    An ESP32-powered, voice-enabled, memory-aware AI plant care system that
    monitors environmental conditions, analyses plant health, and provides
    intelligent care recommendations.
  </em>
</p>

<p align="center">
  <strong>ESP32 Powered · Gemini AI · Live Monitoring · Voice Enabled · Simulator Support</strong>
</p>

---

# 🌿 Overview

Luna is more than a basic plant monitoring system.

It combines an **ESP32 sensor system**, **Python-based health analysis**, **persistent memory**, **Gemini AI**, **voice responses**, **care planning**, and a **self-healing monitoring system**.

Luna can operate in two modes:

- 🧪 **Simulator Mode** — Generates realistic sensor readings without ESP32 hardware.
- 🔌 **Real Hardware Mode** — Reads live data from the ESP32 through USB Serial communication.

This allows the complete AI system to be developed and tested even before the physical hardware is connected.

---

# ✨ Features

## 🧠 AI Plant Analysis

Luna uses Gemini AI to analyse plant and environmental conditions and provide intelligent care recommendations.

The AI receives sensor data together with Luna's rule-based health score.

---

## 📡 Six Sensor Monitoring System

Luna is designed to monitor:

| Sensor | Purpose |
|---|---|
| 🌡️ DHT22 | Temperature and Humidity |
| 💧 Soil Moisture Sensor | Soil moisture level |
| ☀️ LDR Module | Ambient light level |
| 🌧️ Rain Sensor | Rain detection and rain intensity |
| 🌬️ MQ-135 | Air quality monitoring |
| 🌡️ BMP280 | Atmospheric pressure |

---

## 🖥️ OLED Display

A **0.96-inch I2C SSD1306 OLED display** provides local monitoring of:

- Temperature
- Humidity
- Soil Moisture
- Light Level
- Rain Status
- Rain Intensity
- Air Quality
- Atmospheric Pressure

---

## ❤️ Plant Health Scoring

Luna calculates a weighted plant health score from **0 to 100**.

The scoring system considers:

| Parameter | Weight |
|---|---:|
| Temperature | 28 |
| Humidity | 22 |
| Soil Moisture | 20 |
| Air Quality | 15 |
| Rain | 10 |
| Pressure | 5 |
| **Total** | **100** |

### Health Status

| Score | Status |
|---:|---|
| 85–100 | 🟢 Excellent |
| 70–84 | 🔵 Good |
| 50–69 | 🟡 Mild Stress |
| 30–49 | 🟠 Stressed |
| 0–29 | 🔴 Critical |

---

## 🔄 Self-Healing Monitoring

Luna monitors consecutive poor health readings.

```text
HEALTHY
   │
   │ Score below threshold
   ▼
MONITORING
   │
   │ Poor readings continue
   ▼
HEALING
   │
   ├── Detect possible cause
   ├── Generate recommended actions
   ├── Speak alerts
   └── Log incident
   │
   ▼
RECOVERY
```

The current configuration includes:

- Health threshold monitoring
- Consecutive poor reading detection
- AI-assisted recovery recommendations
- Incident logging
- Healing cooldown protection

---

## 🧠 Persistent Memory

Luna stores information including:

- Recent sensor readings
- AI responses
- Care plans
- Health history
- Self-healing incidents

This information persists across program restarts.

---

## 🗣️ Voice Responses

Luna can speak alerts and AI responses using:

```text
pyttsx3
```

Voice can be enabled or disabled through:

```python
VOICE_ENABLED = True
```

The current default voice backend is:

```python
TTS_BACKEND = "pyttsx3"
```

---

## 📅 AI Care Planning

Luna can generate plant care recommendations for different periods of the day:

- 🌅 Morning
- ☀️ Afternoon
- 🌙 Evening

The care plan is stored and checked during operation.

---

## 📊 Live Dashboard

The project includes a Flask-based web dashboard for monitoring:

- Sensor values
- Plant health
- Health trends
- Care plans
- Incidents
- System statistics

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────┐
                         │       ESP32           │
                         │   WROOM-32D 38-Pin    │
                         └───────────┬───────────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
               ▼                     ▼                     ▼
          ┌─────────┐           ┌─────────┐          ┌─────────┐
          │ Sensors │           │  OLED   │          │  USB    │
          │         │           │ Display │          │ Serial  │
          └────┬────┘           └─────────┘          └────┬────┘
               │                                          │
               │                                          ▼
               │                               ┌──────────────────┐
               │                               │  Serial Reader   │
               │                               │     Python       │
               │                               └────────┬─────────┘
               │                                        │
               │                                        ▼
               │                               ┌──────────────────┐
               │                               │  Health Scorer   │
               │                               │     0–100        │
               │                               └────────┬─────────┘
               │                                        │
               │                    ┌───────────────────┼───────────────────┐
               │                    │                   │                   │
               ▼                    ▼                   ▼                   ▼
            Sensors             Memory            Self-Healer          AI Brain
                                                       │                   │
                                                       │                   │
                                                       ▼                   ▼
                                                   Incidents          Gemini AI
                                                                           │
                                                                           ▼
                                                                    Voice Agent
                                                                           │
                                                                           ▼
                                                                       Dashboard
```

---

# 📡 Hardware

## Main Controller

```text
ESP32-WROOM-32D
38-Pin Development Board
```

---

# 🔌 ESP32 Pin Connections

| Component | ESP32 Pin |
|---|---:|
| DHT22 DATA | GPIO 4 |
| Rain Sensor DO | GPIO 27 |
| MQ-135 Analog Output | GPIO 32 |
| Rain Sensor Analog Output | GPIO 33 |
| Soil Moisture Analog Output | GPIO 34 |
| LDR Analog Output | GPIO 35 |
| BMP280 SDA | GPIO 21 |
| BMP280 SCL | GPIO 22 |
| OLED SDA | GPIO 21 |
| OLED SCL | GPIO 22 |

## I2C Bus

The BMP280 and OLED share the same I2C bus:

```text
ESP32 GPIO 21 ───── SDA
ESP32 GPIO 22 ───── SCL
```

---

# 🧩 Complete Sensor Wiring

## DHT22

```text
DHT22 VCC   → 3.3V
DHT22 GND   → GND
DHT22 DATA  → GPIO 4
```

---

## Soil Moisture Sensor

```text
VCC → ESP32 supply
GND → GND
AO  → GPIO 34
```

The soil calibration values can be adjusted in the ESP32 firmware:

```cpp
const int SOIL_DRY_VALUE = 3000;
const int SOIL_WET_VALUE = 1400;
```

These values should be calibrated for the actual sensor and soil.

---

## LDR Module

```text
VCC → ESP32 supply
GND → GND
AO  → GPIO 35
```

---

## Rain Sensor

### Digital Output

```text
DO → GPIO 27
```

### Analog Output

```text
AO → GPIO 33
```

The digital output is used for rain detection.

The analog output is used to estimate rain intensity.

---

## MQ-135 Air Quality Sensor

```text
AO → GPIO 32
GND → GND
```

The MQ-135 requires a warm-up period before readings become more stable.

Current firmware warm-up period:

```text
60 seconds
```

---

## BMP280 Pressure Sensor

```text
VCC → 3.3V
GND → GND
SDA → GPIO 21
SCL → GPIO 22
```

The firmware checks the common BMP280 I2C addresses:

```text
0x76
0x77
```

---

## 0.96" SSD1306 OLED

```text
VCC → 3.3V
GND → GND
SDA → GPIO 21
SCL → GPIO 22
```

Default display configuration:

```text
Resolution: 128 × 64
I2C Address: 0x3C
Driver: SSD1306
```

---

# 🖥️ ESP32 Firmware

The ESP32 firmware reads all connected sensors, updates the OLED display, and sends data to the computer through USB Serial.

The firmware is designed for:

```text
ESP32
↓
Read Sensors
↓
Process Sensor Values
↓
Update OLED
↓
Send Serial Data
↓
Python SerialReader
↓
Health Scoring + AI Analysis
```

---

# 📤 Serial Communication

The Python application and ESP32 communicate through USB Serial.

Current serial settings:

```text
Baud Rate: 9600
```

The project uses a CSV-style sensor communication interface.

The core data required by the Python health and AI pipeline includes:

```text
Temperature
Humidity
Air Quality
Rain Status
Pressure
Soil Moisture
```

The serial format used by the ESP32 firmware and `SerialReader` must always remain synchronized.

> ⚠️ Important: If the ESP32 firmware serial format is changed, update `python/serial_reader.py` accordingly.

---

# 🧪 Simulator Mode

Luna can operate without physical hardware.

In:

```text
python/config.py
```

set:

```python
USE_REAL_HARDWARE = False
```

The simulator generates sensor readings and allows testing of:

- Serial reader
- Health scoring
- Memory
- AI analysis
- Care planning
- Self-healing
- Voice responses

When running in simulator mode, Luna should display:

```text
📡 Hardware Mode: SIMULATOR
📡 Mode: Sensor Simulator
```

---

# 🔌 Real Hardware Mode

When the ESP32 is connected and ready, edit:

```text
python/config.py
```

Set:

```python
USE_REAL_HARDWARE = True
```

Then set the correct serial port:

```python
SERIAL_PORT = "COM3"
```

For example:

```python
USE_REAL_HARDWARE = True
SERIAL_PORT = "COM3"
BAUD_RATE = 9600
```

The correct COM port can be found in:

```text
Arduino IDE
→ Tools
→ Port
```

---

# ⚙️ Hardware Toggle System

Luna supports individual hardware availability settings.

Example:

```python
USE_REAL_HARDWARE = True

HW_DHT22_AVAILABLE = True
HW_MQ135_AVAILABLE = True
HW_RAIN_AVAILABLE = True
HW_BMP280_AVAILABLE = True
HW_SOIL_AVAILABLE = True
```

When a sensor is unavailable, Luna can use configured default values instead of stopping the entire system.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/knox-13/AI-Plant-Monitor.git
```

Enter the project directory:

```bash
cd AI-Plant-Monitor
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

at the beginning of your terminal prompt.

---

## 3. Install Required Packages

```powershell
python -m pip install --no-cache-dir pyserial google-genai python-dotenv schedule pandas requests Flask pyttsx3
```

Optional speech recognition package:

```powershell
python -m pip install --no-cache-dir vosk
```

---

# 🔑 Gemini API Setup

Create a file named:

```text
.env
```

in the project root.

Example:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GROQ_API_KEY=
```

Do not upload or commit your `.env` file.

The `.env` file should remain private.

---

# ▶️ Running Luna

Make sure the virtual environment is active:

```text
(.venv)
```

Then run:

```powershell
python main.py
```

Expected startup:

```text
🌱 Luna — AI Plant Care System
================================
📡 Hardware Mode: SIMULATOR
🌱 Simulated serial port active
📡 Mode: Sensor Simulator
🌱 Luna is awake and listening to her senses...
```

---

# 📊 Running the Dashboard

Open another terminal.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python dashboard/app.py
```

Open the dashboard in your browser:

```text
http://localhost:5000
```

---

# 📁 Project Structure

```text
AI-Plant-Monitor/
│
├── main.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── arduino/
│   └── luna_sensors/
│       └── luna_sensors.ino
│
├── python/
│   ├── config.py
│   ├── ai_brain.py
│   ├── serial_reader.py
│   ├── sensor_simulator.py
│   ├── health_scorer.py
│   ├── memory.py
│   ├── scheduler.py
│   ├── self_healer.py
│   └── voice_agent.py
│
├── dashboard/
│   ├── app.py
│   └── templates/
│       └── index.html
│
├── data/
│   ├── sensor_logs/
│   │   └── sensor_data.csv
│   ├── luna_memory.json
│   ├── care_plan.json
│   └── incidents.json
│
├── piper/
│
└── voice_output/
```

---

# 📦 Dependencies

| Package | Purpose |
|---|---|
| `google-genai` | Gemini AI integration |
| `pyserial` | ESP32 USB Serial communication |
| `python-dotenv` | Loads API keys from `.env` |
| `schedule` | Scheduled tasks |
| `pandas` | Sensor data processing |
| `requests` | HTTP communication |
| `Flask` | Web dashboard |
| `pyttsx3` | Text-to-speech voice |
| `vosk` | Optional offline speech recognition |

---

# ⚙️ Important Configuration

Configuration is located in:

```text
python/config.py
```

## Hardware

```python
USE_REAL_HARDWARE = False

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

READ_INTERVAL_SECONDS = 2
```

## AI

```python
AI_MODEL = "gemini-2.5-flash"

AI_CALL_INTERVAL = 30
MAX_RETRIES = 3
```

## Voice

```python
VOICE_ENABLED = True

TTS_BACKEND = "pyttsx3"

TTS_RATE = 165
TTS_VOLUME = 0.95
```

## Self-Healing

```python
HEALING_THRESHOLD_SCORE = 60

HEALING_TRIGGER_COUNT = 5

HEALING_COOLDOWN_MINUTES = 15
```

---

# 📈 Data Flow

```text
        ESP32 / Simulator
               │
               ▼
        SerialReader
               │
               ▼
        Sensor Validation
               │
        ┌──────┴──────┐
        ▼             ▼
      Memory      Health Scorer
        │             │
        │             ▼
        │         Alerts
        │             │
        ▼             ▼
     AI Brain ← Self-Healer
        │
        ▼
   Gemini Analysis
        │
        ├── Voice Response
        ├── Memory Storage
        ├── Care Advice
        └── Dashboard
```

---

# 🛠️ Development Workflow

Whenever changes are made:

```powershell
git status
```

Stage changes:

```powershell
git add .
```

Create a commit:

```powershell
git commit -m "Describe your changes"
```

Push to your repository:

```powershell
git push
```

Before committing, always check that `.env` is not being uploaded.

---

# 🤝 Contributing

This project is currently developed using a fork-based workflow.

```text
Original Repository
        ↓
      Fork
        ↓
   Development
        ↓
      Commit
        ↓
      Push
        ↓
   Pull Request
```

To contribute:

1. Fork the repository.
2. Create or modify features in your fork.
3. Commit your changes.
4. Push them to your GitHub repository.
5. Open a Pull Request to the original repository.

---

# 🌱 Current Development Status

### Completed

- ✅ ESP32 38-pin hardware design
- ✅ DHT22 support
- ✅ Soil moisture monitoring support
- ✅ LDR monitoring support
- ✅ Rain detection support
- ✅ Rain intensity support
- ✅ MQ-135 air quality support
- ✅ BMP280 pressure support
- ✅ SSD1306 OLED support
- ✅ Sensor simulator
- ✅ Hardware/simulator switching
- ✅ Health scoring
- ✅ Persistent memory
- ✅ Gemini AI integration
- ✅ Voice responses
- ✅ Daily care planning
- ✅ Self-healing monitoring
- ✅ Flask dashboard

### In Progress

- 🔧 Final ESP32 hardware testing
- 🔧 Sensor calibration
- 🔧 Final serial communication verification
- 🔧 Real hardware integration testing

---

# 📄 License

MIT License — free to use, modify, and learn from.

---

<p align="center">
  <strong>🌱 Luna is learning to understand her environment — one sensor reading at a time.</strong>
</p>

<p align="center">
  <em>"I am learning to understand my world... thank you for helping me grow." 🌿</em><br>
  <strong>— Luna</strong>
</p>