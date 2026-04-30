# 🌱 Luna — Phase 2: Virtual Sensor Simulator
### Building Luna's Senses (Without Hardware!)

> **Remember**: Type the code yourself — don't copy-paste! Your fingers build the muscle memory. Your brain builds the understanding. 💪

---

## 🎉 Phase 1 Check — You Passed!

Here's what I verified in your project:

| Item | Status | Note |
|------|--------|------|
| Project folders created | ✅ | `arduino/`, `python/`, `data/`, `voice/`, `dashboard/` |
| Python files created | ✅ | All 9 files in `python/` folder |
| `.env` file | ✅ | Both Gemini AND Groq keys — great backup! |
| `requirements.txt` | ✅ | All 7 packages listed |
| `voice/` subfolders | ✅ | `vosk_model/` and `piper_voices/` ready |
| Git initialized | ✅ | `.git` folder found — pro move! |
| `.gitignore` | ✅ | Good — protects your `.env` from being uploaded |
| `uv` package manager | ✅ | Modern and fast — excellent choice! |

### ⚠️ Two Small Things to Note

1. **`python/mian.py`** — This is a typo! You have both `main.py` (in root) and `mian.py` (in `python/`). You can delete `python/mian.py` — we'll keep the root `main.py`.
2. **`pyproject.toml` says `requires-python = ">=3.14"`** — Python 3.14 doesn't exist yet! Change this to `>=3.11`. Open the file and fix that line.
3. **`voice/vosk_model/` and `voice/piper_voices/` are empty** — That's fine for now! We'll deal with voice tools in Phase 5.

---

## ✅ Phase 2 — Virtual Sensor Simulator

> **Stop after this phase and tell me "Phase 2 done" when finished!**

---

### 🎯 Goal

Build a **Python program that pretends to be your Arduino + sensors**.

It will generate realistic fake sensor data (temperature, humidity, air quality, rain, pressure) and output it in the exact same format that a real Arduino would send over USB.

This way, you can build and test the **entire AI system** without owning any hardware yet.

---

### 🤔 Why Are We Doing This?

Great question — isn't this "cheating"? **Absolutely not.**

This is called **hardware simulation** and it's a real professional technique. NASA does it. Game studios do it. Robotics engineers do it. The reason is simple:

- Hardware can break, be unavailable, or be expensive to test with
- Simulating it lets you develop and test everything in software first
- When real hardware arrives, you swap **one single file** and everything else works

Think of it like a flight simulator — pilots train without a real plane first. You're doing the same thing! 🛫

---

### 🧠 Concepts You'll Learn in This Phase

Before we start, let me explain 3 things:

#### 1. What is a Serial Port?
When a real Arduino sends data to your computer, it uses a **serial port** (like `COM3` on Windows). It sends text line by line, like:
```
TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.2
```
Your Python code reads these lines using the `pyserial` library.

Since we have no Arduino, we'll create a **fake serial object** in Python that behaves identically — same methods, same format.

#### 2. What is `random` in Python?
Python has a built-in `random` module that generates random numbers. We'll use it to make sensor readings feel realistic, not perfectly flat.

For example, temperature doesn't stay at exactly 25°C — it fluctuates between 23°C and 28°C. That's what we'll simulate.

#### 3. What is a CSV file?
CSV = **Comma-Separated Values**. It's the simplest way to store data in a table format. Excel can open it. Python can read/write it easily. Every sensor reading will be saved as one row.

```
timestamp,temperature,humidity,air_quality,rain,pressure
2025-04-27 14:30:00,24.5,62.3,412,0,1013.2
2025-04-27 14:30:05,24.7,61.9,415,0,1013.1
```

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Understand What Each Sensor Measures

Before coding anything, know what you're simulating:

| Sensor | What It Measures | Realistic Range |
|--------|-----------------|-----------------|
| **DHT11** | Temperature (°C) | 18 – 35 °C |
| **DHT11** | Humidity (%) | 30 – 90 % |
| **MQ135** | Air quality (ppm CO₂-equivalent) | 300 – 800 ppm (good), 800–2000 (poor) |
| **Rain sensor** | Is it raining? | 0 = dry, 1 = rain detected |
| **BMP180** | Barometric pressure (hPa) | 980 – 1030 hPa |

> 💡 `ppm` = parts per million. Normal outdoor air is ~400 ppm CO₂. A stuffy room can be 1000+.

---

#### Step 2 — Create the Simulator File

Create a new file at this location:
```
AI Plant Monitor/
└── python/
    └── sensor_simulator.py     ← CREATE THIS FILE
```

Open it in VS Code and start writing. Here is the **structure** (pseudocode) — you must turn this into real Python:

```
PSEUDOCODE — DO NOT COPY THIS. Write Python yourself!

--- IMPORTS ---
Import: random, time, datetime, csv, os, math

--- CONSTANTS (put these near the top) ---
Define: the path to your CSV log file
  → It should be: data/sensor_logs/sensor_data.csv

--- FUNCTION: generate_sensor_reading() ---
Purpose: Returns a dictionary with one fake sensor reading

Steps inside the function:
  1. Get the current hour (0–23) using datetime
  2. Temperature:
     - Base temp = 22°C
     - Add a "time of day" effect: warmer during the day (hours 10-17), cooler at night
       Hint: use math.sin() to create a smooth wave, OR just use if/else for simplicity
     - Add small random noise: ±1.5°C using random.uniform()
     - Round to 1 decimal place
  3. Humidity:
     - Base humidity = 60%
     - Make it inversely related to temperature (hotter = drier)
       Hint: if temp > 28, subtract some humidity; if temp < 22, add some
     - Add ±3% random noise
     - Clamp between 20 and 95 (never go outside realistic range)
     - Round to 1 decimal place
  4. Air quality (MQ135 ppm):
     - Base = 420 ppm
     - Add random noise: ±80 ppm
     - Round to nearest whole number (int)
  5. Rain sensor:
     - 90% of the time: 0 (no rain)
     - 10% of the time: 1 (rain)
     - Hint: use random.random() which gives 0.0 to 1.0
       If the result is less than 0.10, it's raining
  6. Pressure (BMP180):
     - Base = 1013.25 hPa (standard sea level)
     - Add random noise: ±5 hPa
     - Round to 2 decimal places
  7. Timestamp:
     - Use datetime.now() and format as a readable string
  
  Return all of this as a Python dictionary with these keys:
    "timestamp", "temperature", "humidity", "air_quality", "rain", "pressure"

--- FUNCTION: reading_to_serial_string(reading) ---
Purpose: Converts a dictionary reading into Arduino-style text

The format must be EXACTLY:
  TEMP:{temp},HUM:{hum},AIR:{air},RAIN:{rain},PRES:{pres}

Example output:
  TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20

Return this as a string (no newline yet — the caller adds that)

--- FUNCTION: save_to_csv(reading) ---
Purpose: Saves one reading to the CSV log file

Steps:
  1. Check if the folder data/sensor_logs/ exists
     If not, create it (use os.makedirs with exist_ok=True)
  2. Check if the CSV file already exists
     - If it doesn't exist yet, we need to write the header row first
     - If it does exist, just append a new row
  3. Open the CSV file in append mode ("a")
  4. Use csv.DictWriter to write the dictionary as a row
     The fieldnames (column order) should be:
       ["timestamp", "temperature", "humidity", "air_quality", "rain", "pressure"]

--- CLASS: SimulatedSerial ---
Purpose: Pretends to be a real pyserial Serial object

Why a class? Because in Phase 3, your serial_reader.py will call:
  serial.readline()
  serial.close()
  serial.is_open

If we make our SimulatedSerial respond to those same calls, 
Phase 3 code won't need to know if it's real or fake!
This is called "duck typing" — if it walks like a duck and quacks like a duck...

The class needs:
  __init__(self, port="SIMULATED", baudrate=9600):
    - Store port and baudrate
    - Set self.is_open = True
    - Print a friendly message: "🌱 Simulated serial port active on SIMULATED"

  readline(self):
    - Generate one sensor reading using generate_sensor_reading()
    - Save it to CSV using save_to_csv()
    - Convert to serial string using reading_to_serial_string()
    - Add "\n" to the end
    - Encode it as bytes (add .encode("utf-8") at the end)
    - Wait 2 seconds before returning (simulates 2-second sensor interval)
    - Return the encoded bytes

  close(self):
    - Set self.is_open = False
    - Print: "🔌 Simulated serial port closed"

--- MAIN BLOCK (if __name__ == "__main__") ---
Purpose: Test the simulator standalone

Steps:
  1. Create a SimulatedSerial object
  2. Print: "Testing simulator — press Ctrl+C to stop"
  3. Loop forever (while True):
     - Call readline() on the object
     - Decode the bytes back to a string (.decode("utf-8"))
     - Strip whitespace (.strip())
     - Print: f"[SENSOR] {line}"
  4. Handle KeyboardInterrupt (Ctrl+C):
     - Call close() on the object
     - Print: "Simulator stopped."
```

---

#### Step 3 — Run and Test It

With your `uv` virtual environment active, run:
```
uv run python python/sensor_simulator.py
```

You should see output like this every 2 seconds:
```
🌱 Simulated serial port active on SIMULATED
Testing simulator — press Ctrl+C to stop
[SENSOR] TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20
[SENSOR] TEMP:24.8,HUM:61.9,AIR:398,RAIN:0,PRES:1014.10
[SENSOR] TEMP:25.1,HUM:60.4,AIR:421,RAIN:0,PRES:1013.55
```

Press `Ctrl+C` to stop. Then check your `data/sensor_logs/` folder — a `sensor_data.csv` file should have been created!

---

#### Step 4 — Verify the CSV Was Created

Open `data/sensor_logs/sensor_data.csv` in VS Code. It should look like:

```
timestamp,temperature,humidity,air_quality,rain,pressure
2025-04-27 14:30:00,24.5,62.3,412,0,1013.20
2025-04-27 14:30:02,24.8,61.9,398,0,1014.10
2025-04-27 14:30:04,25.1,60.4,421,0,1013.55
```

If you see this — beautiful! Luna now has senses 🌿

---

### 📁 Files Created in This Phase

| File | Purpose |
|------|---------|
| `python/sensor_simulator.py` | The entire virtual hardware |
| `data/sensor_logs/sensor_data.csv` | Auto-created when you run the simulator |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Using `print` to display reading instead of returning from function | Your function should return data, not print it | Use `return` in the function, `print` in the main block |
| Forgetting `.encode("utf-8")` in `readline()` | `pyserial` always returns bytes, not strings | Add `.encode("utf-8")` at the very end |
| Not waiting with `time.sleep(2)` | Output floods too fast to read | Add `time.sleep(2)` inside `readline()` |
| Hardcoding the CSV path | Breaks if you run from a different directory | Use `os.path.join()` and build paths relative to the script |
| Not handling `KeyboardInterrupt` | Terminal shows ugly error on Ctrl+C | Wrap your loop in `try/except KeyboardInterrupt` |
| Making air_quality a float | Real MQ135 gives integer-like values | Use `int()` or `round()` without decimals |

---

### 💡 Bonus Challenge (Optional)

If you finish early and want to go further:

**Add "plant stress events"** — occasionally make readings jump to extreme values, like:
- Temperature suddenly hits 38°C (heat stress)
- Humidity drops below 20% (drought)
- Air quality spikes above 900 ppm (poor ventilation)

This will make your AI brain in Phase 4 more interesting to test — Luna will need to detect and respond to these emergencies!

---

### ✅ How to Know You Did It Right

- [ ] Running `uv run python python/sensor_simulator.py` shows sensor lines every 2 seconds
- [ ] Each line follows the format: `TEMP:xx.x,HUM:xx.x,AIR:xxx,RAIN:x,PRES:xxxx.xx`
- [ ] `data/sensor_logs/sensor_data.csv` is created automatically
- [ ] The CSV has a proper header row and data rows
- [ ] Pressing Ctrl+C stops cleanly with a goodbye message
- [ ] Values are realistic (temp not 500°C, humidity not 200%)

---

### 🎊 Phase 2 Celebration (when you're done!)

You just built **virtual hardware in pure software** — that's an intermediate-level skill! Professional IoT engineers call this "hardware abstraction." You now have:

- A realistic sensor simulator with time-of-day variation
- A CSV data logger
- A `SimulatedSerial` class that can swap seamlessly with real hardware later
- A foundation that every future phase will build on

When your real Arduino arrives one day, all you'll need to change is **one line**: swap `SimulatedSerial()` for `serial.Serial("COM3", 9600)`. Everything else stays the same. That's elegant engineering! 🔥

---

## ⏸️ STOP HERE

> 👉 Build `sensor_simulator.py` step by step.
> 
> Test it. See Luna's "senses" come alive.
> 
> When you're done, type: **"Phase 2 done"** or **"Next"**
> 
> I'll then give you **Phase 3: Python Serial Bridge** 🐍

---

## 🔧 Quick `uv` Reference (Since You're Using It)

| Old `pip/venv` command | Your `uv` equivalent |
|------------------------|----------------------|
| `python -m venv luna_env` | `uv venv` |
| `source luna_env/Scripts/activate` | `uv` handles this internally |
| `pip install pandas` | `uv add pandas` |
| `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| `python script.py` | `uv run python script.py` |

> 💡 `uv` is much faster than pip because it's written in Rust. Great choice for this project!

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 2 of 10*
