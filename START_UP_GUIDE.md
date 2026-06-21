# 🌱 Luna — Setup Guide for Your Friend (Hardware Tester)

> **This guide is for someone testing Luna with a real plant and real hardware.**
> No prior knowledge of the project needed. Follow every step in order.

---

## What You Are Setting Up

Luna is an AI system that:
- Reads sensor data from an Arduino every 2 seconds
- Scores the plant's health (0–100)
- Speaks as the plant using a text-to-speech voice
- Shows a live web dashboard at `http://localhost:5000`
- Generates a daily care plan each morning
- Triggers healing protocols when health stays poor

---

## Part 1 — Computer Setup

### Step 1.1 — What You Need on Your Computer

- Windows 10 or 11 (64-bit)
- Internet connection (for first setup only)
- A USB-A port (for the Arduino)
- Speakers or headphones (for Luna's voice)

---

### Step 1.2 — Install Python (if not already installed)

1. Go to https://python.org/downloads
2. Click "Download Python 3.11" (or newer)
3. Run the installer — **check "Add Python to PATH"** before clicking Install
4. Open PowerShell and verify: `python --version` → should show `Python 3.11.x`

---

### Step 1.3 — Install uv (project package manager)

Open PowerShell:
```powershell
pip install uv
```

Verify: `uv --version` → should show a version number

---

### Step 1.4 — Get the Project

**Option A — Download ZIP (easiest):**
1. Go to the GitHub repo link your friend gives you
2. Click the green **Code** button → **Download ZIP**
3. Extract the ZIP to a folder like `C:\Luna\`

**Option B — Git clone:**
```powershell
git clone https://github.com/YOURFRIEND/AI-Plant-Monitor.git
cd "AI Plant Monitor"
```

---

### Step 1.5 — Install Project Dependencies

Open PowerShell **inside the project folder**:
```powershell
cd "C:\Luna\AI Plant Monitor"
uv sync
```

This installs everything. It will take 1–3 minutes on first run. You will see packages being downloaded.

---

### Step 1.6 — Set Up Your API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with a Google account
3. Click **Create API Key** → copy the key
4. In the project folder, create a file called `.env`:
   ```
   GEMINI_API_KEY=paste_your_key_here
   ```
   Save it. The file has no extension — just `.env`

---

### Step 1.7 — Test Software (No Hardware Yet)

Run Luna in simulator mode first:
```powershell
uv run python main.py
```

You should hear a voice say something about the plant, and see readings printing in the terminal.

In a second PowerShell window:
```powershell
uv run python dashboard/app.py
```

Open your browser: `http://localhost:5000`

You should see the dashboard with live sensor data. If this works, your software is set up correctly.

Press `Ctrl+C` in both terminals to stop.

---

## Part 2 — Arduino Hardware Setup

### Step 2.1 — Install Arduino IDE

1. Go to https://arduino.cc/en/software
2. Download **Arduino IDE 2.x** for Windows
3. Run the installer

---

### Step 2.2 — Install Arduino Libraries

1. Open Arduino IDE
2. Click **Tools → Library Manager** (left sidebar)
3. Search and install each of these:
   - `DHT sensor library` by Adafruit — click Install All when asked about dependencies
   - `Adafruit BMP280 Library` by Adafruit

---

### Step 2.3 — Buy / Gather the Hardware

| Item | Search term on Amazon/Robu | Approx Price |
|------|---------------------------|-------------|
| Arduino Uno | "Arduino Uno CH340 clone" | ₹350–450 |
| DHT22 module | "DHT22 temperature humidity module" | ₹150 |
| MQ-135 | "MQ-135 air quality sensor module" | ₹120 |
| Rain sensor | "FC-37 rain detection module" | ₹80 |
| BMP280 | "BMP280 I2C barometric pressure module" | ₹120 |
| Capacitive soil sensor | "capacitive soil moisture sensor v1.2" | ₹80 |
| Jumper wires | "jumper wire male female 40pcs" | ₹80 |
| USB-B cable | "Arduino USB cable" | ₹80 |
| **Total** | | **₹1,060** |

> ⚠️ Buy **capacitive** soil sensor (brown PCB, no metal probes). NOT the resistive one (blue PCB with metal rods) — those corrode in soil within weeks.

---

### Step 2.4 — Wire the Sensors

Use these exact connections:

#### DHT22 (Temperature + Humidity)
```
DHT22 pin VCC  →  Arduino 5V
DHT22 pin GND  →  Arduino GND
DHT22 pin DATA →  Arduino Digital Pin 2
```

#### MQ-135 (Air Quality)
```
MQ-135 VCC   →  Arduino 5V
MQ-135 GND   →  Arduino GND
MQ-135 AOUT  →  Arduino Analog A0
(DO pin is unused)
```

#### Rain Sensor
```
Rain VCC  →  Arduino 3.3V  (important: NOT 5V)
Rain GND  →  Arduino GND
Rain DO   →  Arduino Digital Pin 4
```

#### BMP280 (Pressure) — I2C
```
BMP280 VCC  →  Arduino 3.3V
BMP280 GND  →  Arduino GND
BMP280 SDA  →  Arduino A4
BMP280 SCL  →  Arduino A5
```

#### Capacitive Soil Sensor
```
Soil VCC   →  Arduino 3.3V
Soil GND   →  Arduino GND
Soil AOUT  →  Arduino Analog A1
```

**Don't have a sensor?** That is fine. In `python/config.py`, set that sensor's `HW_*_AVAILABLE = False`. Luna will use a safe default value.

---

### Step 2.5 — Upload the Firmware

1. Plug Arduino into your computer via USB
2. Open Arduino IDE
3. File → Open → navigate to `arduino/luna_sensors/luna_sensors.ino`
4. **Tools → Board → Arduino Uno**
5. **Tools → Port** → select the port that says "Arduino Uno" (e.g. COM3 or COM5)
6. Click the **Upload** button (→ arrow at top)
7. Wait for "Done uploading" message

**Verify it works:**
- Tools → Serial Monitor → set baud rate to **9600**
- You should see CSV lines appearing every 2 seconds:
  ```
  # BMP280 detected
  # Luna sensor firmware ready. Warming up MQ-135...
  24.30,62.10,450,0,1013.50,58.20
  24.28,62.12,449,0,1013.52,58.18
  ```
- Close Serial Monitor after verifying (Luna needs the port)

**Note your COM port** (e.g. `COM3`) — you need it in the next step.

---

## Part 3 — Connect Luna to Real Hardware

### Step 3.1 — Configure the Project

Open `python/config.py` in any text editor (Notepad, VS Code, etc.) and change:

```python
# Line ~16 in config.py
USE_REAL_HARDWARE = True     # ← change from False to True

# Line ~23
SERIAL_PORT = "COM3"         # ← change to your actual COM port
```

If you don't have every sensor wired, set the missing ones:
```python
HW_SOIL_AVAILABLE  = False   # if soil sensor not connected
HW_RAIN_AVAILABLE  = False   # if rain sensor not connected
```

---

### Step 3.2 — Test Each Module

Run these one at a time to confirm each module works:

```powershell
# 1. Test serial reader — should print real sensor values
uv run python python/serial_reader.py

# 2. Test health scorer
uv run python python/health_scorer.py

# 3. Test voice
uv run python python/voice_agent.py
```

For the voice test, you should **hear Luna speak** through your speakers.

---

### Step 3.3 — Run the Full System

**Terminal 1 — Luna's AI brain:**
```powershell
uv run python main.py
```

Expected output in the first 30 seconds:
```
🌱 Luna — AI Plant Care System
🔌 Hardware Mode: REAL ARDUINO
   DHT22 (Temp+Hum)       ✅ ACTIVE  (Pin 2)
   ...
📡 Mode: Real Arduino on COM3
📅 Generating today's care plan...
📡 Reading #1: Temp=24.3°C, Hum=62.1%
🟢 Health Score: 88/100 — EXCELLENT
   Temp=22.0pt  Hum=22pt  Soil=18pt  AQI=15pt  Rain=8pt  Pres=5pt
```

**Terminal 2 — Dashboard:**
```powershell
uv run python dashboard/app.py
```

Open: `http://localhost:5000`

The badge at the top right should say **REAL HARDWARE** (not SIMULATOR).

---

## Part 4 — What to Test and Record

### Checklist for your test session

- [ ] Voice speaks at startup
- [ ] Dashboard shows real sensor values (not all zeros or defaults)
- [ ] Temperature matches a room thermometer within 2°C
- [ ] Soil sensor reads correctly (finger test: feel it vs reading)
- [ ] Health score changes when you breathe on the DHT22 (raises humidity)
- [ ] Dashboard chart builds up over 10 minutes
- [ ] Care plan appears (with morning/afternoon/evening tasks)

### How to trigger a healing test

Temporarily change in `config.py`:
```python
HEALING_THRESHOLD_SCORE = 95   # very high — everything triggers "poor"
HEALING_TRIGGER_COUNT   = 3    # trigger faster
```

Run `main.py` — healing protocol should trigger within 10 seconds. Luna speaks an emergency message.

Change the values back afterwards:
```python
HEALING_THRESHOLD_SCORE = 60
HEALING_TRIGGER_COUNT   = 5
```

---

## Part 5 — Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| "Failed to open COM3" | Wrong port — check Arduino IDE → Tools → Port |
| DHT22 reads `nan` | Check DATA wire is on Pin 2, not Pin 3 |
| All AQI readings = 450 | MQ-135 warming up — wait 60 seconds after power-on |
| No voice | Check speakers are on. Run `uv run python python/voice_agent.py` to test |
| Dashboard shows no data | Make sure `main.py` is also running in another terminal |
| "ModuleNotFoundError" | Run `uv sync` again — a package may not have installed |
| Soil always reads 55% | `HW_SOIL_AVAILABLE = False` in config — set to True |
| Serial Monitor shows nothing | Check baud rate is 9600, check correct port |

---

## Part 6 — Data Location

All data is saved automatically:

| File | Contents |
|------|---------|
| `data/sensor_logs/sensor_data.csv` | Every sensor reading |
| `data/luna_memory.json` | AI responses + rolling readings |
| `data/care_plan.json` | Today's AI-generated care plan |
| `data/incidents.json` | All healing events (open + resolved) |

After your test session, **zip the entire `data/` folder** and send it back — it's valuable real-world data.

---

## Quick Reference Card

```
START LUNA:
  Terminal 1:  uv run python main.py
  Terminal 2:  uv run python dashboard/app.py
  Browser:     http://localhost:5000

STOP LUNA:
  Press Ctrl+C in each terminal

TEST VOICE:
  uv run python python/voice_agent.py

CHECK DATA:
  data/sensor_logs/sensor_data.csv
  data/incidents.json

CHANGE HARDWARE MODE:
  Edit python/config.py → USE_REAL_HARDWARE = True/False
```

---

*Luna AI Plant Care System — Friend / Hardware Tester Setup Guide · June 2026*
