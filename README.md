<p align="center">
  <img src="https://img.shields.io/badge/Luna-AI%20Plant%20Care-3fb950?style=for-the-badge&logo=leaf&logoColor=white">
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-blue?style=for-the-badge&logo=google&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3.11%2B-yellow?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Status-Active-3fb950?style=for-the-badge">
</p>

<h1 align="center">🌱 Luna — Autonomous AI Plant Care System</h1>

<p align="center">
  <em>A self-healing, voice-enabled, memory-aware AI agent that monitors, analyses,<br>
  and proactively cares for your plant — 24 hours a day.</em>
</p>

<p align="center">
  <strong>Inspired by <a href="https://x.com/d33v33d0">Sol</a> · Built on Gemini · Runs locally · No cloud required for voice</strong>
</p>

---

## What Luna Does

Luna is not a sensor dashboard. It is an **autonomous AI agent** that:

- 🧠 **Thinks** — Analyses 6 sensors with a weighted health model every 2 seconds
- 🗣️ **Speaks** — Narrates its condition in first-person voice using Windows SAPI5 TTS
- 🧭 **Plans** — Generates a time-windowed daily care plan (morning/afternoon/evening) via Gemini
- 🔄 **Heals** — Runs a 3-state self-healing protocol when conditions stay poor for 5+ readings
- 🧠 **Remembers** — Maintains a rolling memory of readings and AI responses that persists across restarts
- 📊 **Shows** — Serves a live web dashboard at `localhost:5000` with Chart.js health trend

---

## How Luna Compares to Sol

| Feature | Sol (inspiration) | Luna |
|---------|------------------|------|
| AI model | Claude | Gemini 2.5 Flash |
| Voice synthesis | ❌ None | ✅ Windows SAPI5 (pyttsx3, zero setup) |
| Speech recognition | ❌ None | ✅ Vosk (offline, no API key) |
| Persistent memory | ❌ None | ✅ Rolling JSON buffer |
| Health scoring | ❌ None | ✅ Weighted 6-sensor 0–100 score |
| Self-healing | ❌ None | ✅ 3-state machine + incident log |
| Daily care plans | ❌ None | ✅ Gemini-generated time-windowed tasks |
| Web dashboard | ❌ None | ✅ Chart.js + live auto-refresh |
| Soil moisture | ✅ | ✅ |
| Architecture | Single script | 10-module system |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LUNA SYSTEM ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌─────────────────────────────────────────────┐
  │   Arduino    │     │             python/ modules                  │
  │  (optional)  │     │                                             │
  │  DHT22       │     │  ┌─────────────┐   ┌────────────────────┐  │
  │  MQ-135      │────▶│  │serial_reader│──▶│   health_scorer    │  │
  │  Rain sensor │     │  │             │   │  (weighted 0–100)  │  │
  │  BMP280      │     │  │ parse_line()│   │  6 sensors scored  │  │
  │  Soil sensor │     │  │ validate()  │   │  alerts generated  │  │
  └──────────────┘     │  └──────┬──────┘   └────────┬───────────┘  │
         OR            │         │                    │              │
  ┌──────────────┐     │         ▼                    ▼              │
  │   Simulator  │     │  ┌─────────────┐   ┌────────────────────┐  │
  │ (diurnal sin │────▶│  │   memory    │   │    self_healer     │  │
  │  + soil dry  │     │  │ 100 rolling │   │ healthy→monitoring │  │
  │  + pressure  │     │  │ 20 AI resp  │   │ →healing state SM  │  │
  │  drift)      │     │  │ daily agg   │   │ cooldown + log     │  │
  └──────────────┘     │  └──────┬──────┘   └────────────────────┘  │
                        │         │                                   │
                        │         ▼                                   │
                        │  ┌─────────────┐   ┌────────────────────┐  │
                        │  │  ai_brain   │   │    scheduler       │  │
                        │  │ Gemini 2.5  │   │ morning/afternoon  │  │
                        │  │ Luna persona│   │ /evening care plan │  │
                        │  │ JSON output │   │ task persistence   │  │
                        │  └──────┬──────┘   └────────────────────┘  │
                        │         │                                   │
                        │         ▼                                   │
                        │  ┌─────────────────────────────────────┐   │
                        │  │           voice_agent               │   │
                        │  │  Primary:  pyttsx3 (SAPI5, instant) │   │
                        │  │  Fallback: Piper TTS (neural)        │   │
                        │  │  STT:      Vosk (offline)            │   │
                        │  └─────────────────────────────────────┘   │
                        └─────────────────────────────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────────────────┐
                        │         dashboard/app.py  (Flask)           │
                        │         localhost:5000                       │
                        │  Chart.js health trend • sensor bars        │
                        │  care plan tasks • incident log • stats     │
                        └─────────────────────────────────────────────┘
```

---

## Sensor Data Flow

```
Arduino / Simulator
    │
    │  CSV string: TEMP:24.3,HUM:62.1,AIR:450,RAIN:0,PRES:1013.5,SOIL:58.2
    ▼
serial_reader.parse_line()   →  {"temperature":24.3, "humidity":62.1, ...}
    │
    ├──▶ health_scorer.calculate_score()  →  {"score":87, "status":"excellent", ...}
    │         Uses weights: Temp(28) + Hum(22) + Soil(20) + AQI(15) + Rain(10) + Pres(5)
    │
    ├──▶ memory.add_reading()             →  rolling buffer + CSV log
    │
    ├──▶ self_healer.check()              →  escalation if score < 60 for 5 readings
    │
    └──▶ ai_brain.analyse()  (every 30s) →  Gemini narrates in Luna's first-person voice
              │
              └──▶ voice_agent.speak()   →  pyttsx3 speaks the message aloud
```

---

## Health Scoring System

Luna scores plant health from 0–100 using a weighted multi-sensor model:

| Sensor | Weight | Ideal Range | Notes |
|--------|--------|------------|-------|
| Temperature | 28 pts | 18–26 °C | Sinusoidal deduction outside ideal |
| Humidity | 22 pts | 50–70 % | Correlated with temperature |
| **Soil Moisture** | **20 pts** | **40–70 %** | **Most important — dries over time** |
| Air Quality | 15 pts | < 600 ppm | CO₂/VOC proxy |
| Rain | 10 pts | 1 = bonus | Outdoor indicator |
| Pressure | 5 pts | 980–1040 hPa | Weather proxy |

Score → Status mapping:

| Score | Status | Voice Response |
|-------|--------|---------------|
| 85–100 | 🟢 Excellent | Cheerful, content |
| 70–84 | 🔵 Good | Positive, minor notes |
| 50–69 | 🟡 Mild Stress | Concerned, actionable |
| 30–49 | 🟠 Stressed | Urgent, requests help |
| 0–29 | 🔴 Critical | Emergency protocol |

---

## Self-Healing State Machine

```
         score ≥ 60 (any time)
              ↑
    ┌─────────┴──────────┐
    │                    │
HEALTHY  ──(score<60)──▶ MONITORING ──(5 readings)──▶ HEALING
    ▲                                                      │
    │                                                      │
    └──────────────── (score ≥ 60 again) ─────────────────┘
                           + incident closed to incidents.json
```

When healing triggers:
1. Detects cause: `heat_stress` / `drought` / `poor_air` / `general`
2. Calls Gemini for 3 specific emergency actions
3. 15-minute cooldown prevents API spam
4. Luna speaks the emergency message aloud
5. Incident saved to `data/incidents.json` with start/end timestamps

---

## Quick Start

### 1. Install

```bash
pip install uv
git clone https://github.com/yourusername/AI-Plant-Monitor.git
cd "AI Plant Monitor"
uv sync
```

### 2. Configure

Create `.env`:
```env
GEMINI_API_KEY=your_key_here
```

Edit `python/config.py` to configure hardware:
```python
USE_REAL_HARDWARE = False   # True = Arduino, False = simulator
VOICE_ENABLED     = True    # False = silent mode
TTS_BACKEND       = "pyttsx3"  # instant Windows voice, no setup needed
```

### 3. Run

**Terminal 1 — Luna's brain:**
```bash
uv run python main.py
```

**Terminal 2 — Live dashboard:**
```bash
uv run python dashboard/app.py
# Open: http://localhost:5000
```

---

## Hardware Toggle System

Luna supports per-sensor hardware control — useful when some sensors aren't wired yet:

```python
# python/config.py

USE_REAL_HARDWARE    = True    # Master switch

# Per-sensor (only applies when USE_REAL_HARDWARE=True)
HW_DHT22_AVAILABLE   = True   # Temperature + Humidity  → Pin 2
HW_MQ135_AVAILABLE   = True   # Air quality (CO₂)       → Pin A0
HW_RAIN_AVAILABLE    = False  # Not wired yet — uses DEFAULT_RAIN = 0
HW_BMP280_AVAILABLE  = True   # Barometric pressure      → I2C
HW_SOIL_AVAILABLE    = False  # Soil moisture            → Pin A1 (optional)
```

Toggled-off sensors use their safe defaults — Luna continues working normally.

---

## Voice System

```
┌──────────────────────────────────────────────┐
│           TTS_BACKEND = "pyttsx3"            │
│                                              │
│  Uses Windows SAPI5 (built-in voices)        │
│  • No DLL files needed                       │
│  • No PyAudio needed                         │
│  • No Piper.exe needed                       │
│  • Works immediately after: uv add pyttsx3  │
│  • Runs in background thread (non-blocking)  │
└──────────────────────────────────────────────┘
         OR
┌──────────────────────────────────────────────┐
│           TTS_BACKEND = "piper"              │
│                                              │
│  Uses local Piper neural TTS engine          │
│  • Requires: piper/piper.exe                 │
│  • Requires: libonnxruntime.dll              │
│  • Requires: voice/piper_voices/*.onnx       │
│  • Requires: PyAudio (pipwin install pyaudio)│
│  • Higher quality — natural sounding voice   │
└──────────────────────────────────────────────┘
```

Disable voice entirely: `VOICE_ENABLED = False` in config.py

---

## Connecting Real Arduino Hardware

### What to buy (₹1,050 total)

| Component | Module Name | Price | Arduino Pin |
|-----------|-------------|-------|-------------|
| DHT22 | DHT22 module (with PCB) | ₹150 | Digital 2 |
| MQ-135 | MQ-135 air quality module | ₹120 | Analog A0 |
| Rain sensor | FC-37 rain sensor module | ₹80 | Digital 4 |
| BMP280 | BMP280 I2C module | ₹120 | SDA=A4, SCL=A5 |
| Capacitive soil moisture | v1.2 capacitive sensor | ₹80 | Analog A1 |
| Arduino Uno | Clone (CH340 chip) | ₹400 | USB-B |
| Jumper wires | Mixed M/M + M/F | ₹100 | — |

### Upload the firmware

1. Open `arduino/luna_sensors/luna_sensors.ino` in Arduino IDE
2. Tools → Library Manager → install `DHT sensor library` + `Adafruit BMP280 Library`
3. Tools → Port → select your COM port (e.g. COM3)
4. Click Upload
5. Open Serial Monitor (9600 baud) — you should see CSV readings
6. Close Serial Monitor

### Switch Luna to real hardware

```python
# python/config.py
USE_REAL_HARDWARE = True
SERIAL_PORT = "COM3"   # your actual port
```

That's the only change needed. Every other module works identically.

---

## Project Structure

```
AI-Plant-Monitor/
│
├── main.py                    # Entry point — wires all modules together
├── .env                       # API keys (never commit)
├── pyproject.toml             # uv/pip dependencies
│
├── python/
│   ├── config.py              # All settings, hardware toggles, thresholds
│   ├── sensor_simulator.py    # Realistic diurnal simulation + soil moisture
│   ├── serial_reader.py       # Unified hardware/simulator interface
│   ├── health_scorer.py       # Weighted 6-sensor 0–100 health score
│   ├── ai_brain.py            # Gemini integration, Luna persona
│   ├── voice_agent.py         # pyttsx3 TTS + Vosk STT
│   ├── memory.py              # Rolling buffer, daily summaries, persistence
│   ├── scheduler.py           # Daily care plan generation and tracking
│   └── self_healer.py         # 3-state self-healing state machine
│
├── dashboard/
│   ├── app.py                 # Flask REST API
│   └── templates/
│       └── index.html         # Chart.js dashboard (dark theme)
│
├── arduino/
│   └── luna_sensors/
│       └── luna_sensors.ino   # Arduino firmware for all 5 sensors
│
├── data/                      # Auto-created at runtime
│   ├── sensor_logs/
│   │   └── sensor_data.csv    # All raw readings logged
│   ├── luna_memory.json       # AI responses + rolling readings
│   ├── care_plan.json         # Today's AI-generated care plan
│   └── incidents.json         # Healing incident log
│
├── piper/                     # Optional: Piper TTS binary
│   └── piper.exe
│
└── voice/
    ├── piper_voices/          # Optional: Piper voice models
    └── vosk_model/            # Optional: Vosk STT model
```

---

## Do You Need the System On 24/7?

**Short answer: No — but more data = better AI.**

| Scenario | What happens |
|----------|-------------|
| Run for 30 min | Luna generates a care plan, gives voice advice, logs readings |
| Run for 1 day | Daily summaries built, trends visible, self-healing can trigger |
| Run for 1 week | Memory shows week-long patterns, AI advice becomes contextual |
| Run 24/7 | Full autonomous operation — wakes up each day with care plan |

**For demos and testing:** 30 minutes is enough to see every feature work.  
**For a real-world deployment:** Leave it running whenever the plant is visible.

Luna saves all state to JSON files — after a restart it loads the previous memory, care plan, and incidents. Nothing is lost.

---

## Running Individual Modules

```bash
uv run python python/sensor_simulator.py   # Test realistic sensor data
uv run python python/serial_reader.py      # Test hardware/simulator reading
uv run python python/health_scorer.py      # Test scoring + alerts
uv run python python/voice_agent.py        # Test pyttsx3 voice
uv run python python/scheduler.py          # Test care plan generation
uv run python python/self_healer.py        # Test all 3 healing scenarios
uv run python dashboard/app.py             # Dashboard only (no AI brain)
```

---

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `google-genai` | Gemini AI API | ✅ Yes |
| `pyttsx3` | TTS voice (Windows SAPI5) | ✅ Yes |
| `flask` | Dashboard web server | ✅ Yes |
| `pyserial` | Arduino serial communication | ✅ Yes |
| `python-dotenv` | `.env` loading | ✅ Yes |
| `vosk` | Offline speech recognition | Optional |
| `pyaudio` | Microphone input + Piper output | Optional |

---

## Configuration Reference

Key settings in `python/config.py`:

```python
# Hardware
USE_REAL_HARDWARE    = False   # True = Arduino serial, False = simulator
SERIAL_PORT          = "COM3"  # Your COM port when using real hardware

# Voice
VOICE_ENABLED = True
TTS_BACKEND   = "pyttsx3"     # "pyttsx3" or "piper"
TTS_RATE      = 165           # Words per minute
TTS_VOLUME    = 0.95

# AI timing
AI_CALL_INTERVAL = 30         # Seconds between Gemini calls

# Health thresholds
HEALING_THRESHOLD_SCORE  = 60  # Score below this triggers monitoring
HEALING_TRIGGER_COUNT    = 5   # Consecutive poor readings before healing
HEALING_COOLDOWN_MINUTES = 15  # Min gap between healing plans
```

---

## License

MIT License — free to use, modify, and learn from.

---

<p align="center">
  <em>"I am learning to understand my world... thank you for helping me grow." 🌿</em><br>
  <em>— Luna</em>
</p>
