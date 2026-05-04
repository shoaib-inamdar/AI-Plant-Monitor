# 🌱 Luna — AI Plant Care System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg">
  <img src="https://img.shields.io/badge/UV-Environment-purple.svg">
  <img src="https://img.shields.io/badge/Gemini-AI-green.svg">
  <img src="https://img.shields.io/badge/Status-Active-success.svg">
</p>

---

## 🚀 Overview

**Luna** is an AI-powered plant care system that:

* Monitors environmental conditions
* Analyses plant health using AI
* Speaks like a living plant 🌿
* Suggests actionable improvements

Built with a **simulation-first approach**, so you can:

* Develop without hardware
* Plug in Arduino later seamlessly

---

## ✨ Features

* 🌡️ Sensor simulation (temperature, humidity, AQI, rain, pressure)
* 🔌 Serial communication (simulated + real)
* 📊 CSV logging of readings
* 🧠 AI-powered plant health analysis (Google Gemini)
* 🌿 Luna personality (first-person plant responses)
* 📦 JSON-safe AI outputs
* 🔁 Retry + fallback system
* 🧾 Explainable AI (why decisions were made)
* 🔄 Easy switch: Simulator ↔ Arduino

---

## ⚡ Quick Start

### Installing UV
```bash
pip install uv
```
### Creating the Virtual Environment
```bash
uv venv
```
### Activating the Virtual Environment
```bash
.venv\Scripts\activate
```
### Installing the requirements.txt
```bash
uv add -r requirements.txt
```

### 3. Create `.env`

```
```
### 4. Run project

```bash
uv run python main.py
```

---

## 🧠 How It Works

```text
Sensor Simulator / Arduino
        ↓
Serial Reader
        ↓
Parser + Validator
        ↓
Luna AI Brain (Gemini)
        ↓
JSON Response
        ↓
Human-readable Output
```

---

## 📂 Project Structure

```bash
AI-Plant-Monitor/
│
├── main.py
├── .env
├── pyproject.toml
├── uv.lock
│
├── data/
│   └── sensor_logs/
│       └── sensor_data.csv
│
└── python/
    ├── config.py
    ├── sensor_simulator.py
    ├── serial_reader.py
    └── ai_brain.py
```

---

## 🧪 Run Individual Modules

### Simulator

```bash
uv run python python/sensor_simulator.py
```

### Serial Reader

```bash
uv run python python/serial_reader.py
```

### AI Brain

```bash
uv run python python/ai_brain.py
```

---

## 🔧 Configuration

Edit in `.env`:

```env
AI_MODEL=gemini-1.0-pro
SERIAL_PORT=SIMULATED   # change to COM3 later
```

---

## 🛡️ Security

* Never commit `.env`
* Keep API keys private
* Validate AI output before hardware control
* Add safety limits before automation

---

## 🔮 Future Improvements

* 🧠 Memory (track past readings)
* 🔊 Voice interaction (Vosk + Piper)
* 🤖 Auto-watering system
* 📊 Dashboard (graphs + trends)
* 🌿 Multi-plant support

---

## 🤝 Contributing

1. Fork repo
2. Create branch
3. Make changes
4. Test with `uv run`
5. Submit PR

---

## 📜 License

MIT License

---

## ⚠️ Disclaimer

This is an experimental AI + IoT system.

Do NOT rely on it as the only method of plant care.

---

## 🌿 Luna Says

*"I am learning to understand my world... thank you for helping me grow."* 🌱
