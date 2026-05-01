# 🌱 Luna — Phase 3: The Python Serial Bridge
### Teaching Luna to Actually Hear Her Sensors 🎧

> **Remember the rule**: Read the pseudocode, understand it, then type your Python yourself. No copy-pasting! 💪

---

## 🎉 Phase 2 Check — You Passed!

Here's what I verified:

| Check | Status | Note |
|-------|--------|------|
| `sensor_simulator.py` structure | ✅ | All 3 functions + class correctly built |
| Temperature day/night variation | ✅ | Logic works perfectly |
| `SimulatedSerial` class | ✅ | All methods correct, `is_open` guard added |
| CSV created automatically | ✅ | 34 rows of real data |
| CSV header row | ✅ | Correct column names |
| Pressure decimal inconsistency | 🔧 Fixed | Added `float(f"{pressure:.2f}")` — now always 2 decimals |
| Git committed & pushed | ✅ | Excellent habit! Keep doing this every phase |

**You also deleted `python/mian.py`** — noticed that too. Well spotted! 🙌

---

## ✅ Phase 3 — The Python Serial Bridge

> **Stop after this phase and tell me "Phase 3 done" when finished!**

---

### 🎯 Goal

Build `serial_reader.py` — the **middleman** between your sensor simulator and every other part of the system.

Right now you have raw strings like:
```
TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20
```

By the end of Phase 3, you'll convert these into clean Python dictionaries like:
```python
{
    "timestamp": "2026-04-30 21:30:00",
    "temperature": 24.5,
    "humidity": 62.3,
    "air_quality": 412,
    "rain": 0,
    "pressure": 1013.20,
    "status": "ok"
}
```

And you'll also update `config.py` and `main.py` so everything is connected.

---

### 🤔 Why Is This Phase Important?

Imagine a phone call. The Arduino (or simulator) speaks in a raw foreign language:
```
TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20
```

Your Python code speaks in dictionaries and objects. You need a **translator in the middle**.

That translator is `serial_reader.py`. Every future phase (AI brain, voice agent, health scorer) will ask it:
> "Hey, what are the latest sensor readings?"

And it will give back a clean, validated, ready-to-use dictionary. No messy string parsing scattered everywhere.

This is called **separation of concerns** — each file has one clear job. It's a core principle of good software design.

---

### 🧠 Three Concepts to Understand First

#### 1. String Parsing
Your raw data looks like this:
```
TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20
```
Parsing means splitting it apart and extracting the values. Example approach:
- Split by `,` → `["TEMP:24.5", "HUM:62.3", "AIR:412", "RAIN:0", "PRES:1013.20"]`
- Split each by `:` → `["TEMP", "24.5"]`, `["HUM", "62.3"]`, etc.
- Convert to numbers: `float("24.5")` → `24.5`

#### 2. Data Validation
Sensors can sometimes send garbage. A real temperature reading of `999.9°C` means something broke. Validation means checking: "Is this reading physically possible?"

If a value is impossible, we mark the reading with `"status": "error"` instead of passing bad data to the AI.

#### 3. Exception Handling with `try/except`
When parsing strings, things can go wrong:
- What if the Arduino sends a half-line? `TEMP:24.5,HUM:`
- What if a number is corrupted? `TEMP:24.X`

`try/except` is Python's safety net. If something breaks inside `try`, the `except` block catches it gracefully instead of crashing the whole program.

```
try:
    risky operation here
except SomeError:
    handle it safely here
```

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py` First

Before building the reader, set up your config file. This is where all settings live — one central place to change things.

Open `python/config.py` and write it based on this structure:

```
PSEUDOCODE for config.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: os
Import load_dotenv from dotenv

--- LOAD .env FILE ---
Call load_dotenv() so Python can read your .env keys

--- SERIAL SETTINGS ---
SERIAL_PORT = "SIMULATED"         # Change to "COM3" when real Arduino arrives
BAUD_RATE = 9600                  # Standard Arduino baud rate
READ_INTERVAL_SECONDS = 2         # How often to read from sensor

--- API KEYS (read from .env, never hardcode!) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

--- AI SETTINGS ---
AI_MODEL = "gemini-1.5-flash"     # Which model to use
USE_BACKUP_AI = False             # Set to True to switch to Groq

--- SENSOR THRESHOLDS (for validation) ---
These define what's "realistic" for each sensor:
TEMP_MIN = 0         # °C — below this is definitely wrong
TEMP_MAX = 50        # °C — above this is definitely wrong
HUM_MIN = 10         # %
HUM_MAX = 100        # %
AQI_MIN = 200        # ppm
AQI_MAX = 3000       # ppm
PRES_MIN = 900       # hPa
PRES_MAX = 1100      # hPa

--- FILE PATHS ---
CSV_LOG_PATH = "data/sensor_logs/sensor_data.csv"
MEMORY_FILE_PATH = "data/luna_memory.json"
```

> 💡 Why put thresholds in config? Because later you might want to change what counts as "too hot" or "too humid" without hunting through multiple files.

---

#### Step 2 — Build `serial_reader.py`

Open `python/serial_reader.py`. This is the main file for this phase.

```
PSEUDOCODE for serial_reader.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: sys, os, datetime
Import: your SimulatedSerial from sensor_simulator
Import: everything from config (or specific values)

--- CLASS: SerialReader ---

  __init__(self, use_simulator=True):
    This is where we decide: real Arduino or simulated?
    
    If use_simulator is True:
      - Create a SimulatedSerial object, store as self.serial
      - Print: "📡 Using simulated sensor data"
    
    If use_simulator is False:
      (This is for when real hardware arrives — Phase hardware upgrade!)
      - Import serial (pyserial) — do this import INSIDE this block
        Why? Because if someone doesn't have pyserial, it only fails when
        they try to use real hardware, not when they just import this file
      - Try to create: serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
      - Store it as self.serial
      - Print: f"📡 Connected to real Arduino on {SERIAL_PORT}"
      - If it fails (SerialException), print an error and exit
    
    Set self.last_reading = None   (store the most recent valid reading)

  ---

  read_raw_line(self):
    Purpose: Get one raw line of bytes from the serial port
    
    Steps:
      1. Check if self.serial.is_open — if not, return None
      2. Try:
         - Call self.serial.readline()
         - Decode from bytes to string (.decode("utf-8"))
         - Strip whitespace (.strip())
         - If the result is an empty string, return None
         - Return the stripped string
      3. Except any Exception:
         - Print: f"⚠️ Error reading serial line: {error}"
         - Return None

  ---

  parse_line(self, raw_line):
    Purpose: Convert "TEMP:24.5,HUM:62.3,AIR:412,RAIN:0,PRES:1013.20"
             into a clean Python dictionary
    
    Expected format: "KEY:value,KEY:value,KEY:value,..."
    
    Steps:
      Wrap everything in try/except — if parsing fails, return None
      
      1. Split raw_line by "," → you get a list of "KEY:value" strings
      2. Create an empty dictionary called data = {}
      3. Loop through each "KEY:value" pair:
         - Split by ":" → gives you [key, value]
         - Strip whitespace from key and value
         - Store in data dictionary: data[key] = value
      
      4. Now extract and convert each value:
         - temperature = float(data["TEMP"])
         - humidity = float(data["HUM"])
         - air_quality = int(data["AIR"])
         - rain = int(data["RAIN"])
         - pressure = float(data["PRES"])
      
      5. Add a timestamp (current time):
         - timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
      6. Return a dictionary with keys:
         "timestamp", "temperature", "humidity", 
         "air_quality", "rain", "pressure"
      
      If ANYTHING above raises an exception:
        - Print: f"⚠️ Failed to parse line: '{raw_line}' — {error}"
        - Return None

  ---

  validate_reading(self, reading):
    Purpose: Check if a parsed reading has physically realistic values
    
    If reading is None: return None
    
    Check each value against thresholds from config:
      - TEMP_MIN <= temperature <= TEMP_MAX
      - HUM_MIN <= humidity <= HUM_MAX
      - AQI_MIN <= air_quality <= AQI_MAX
      - PRES_MIN <= pressure <= PRES_MAX
      - rain must be either 0 or 1
    
    If ALL checks pass:
      - Add "status": "ok" to the reading dictionary
      - Return the reading
    
    If ANY check fails:
      - Print which value failed and what the value was
      - Add "status": "error" to the reading dictionary
      - Still return the reading (don't throw it away — 
        the AI brain might want to know a sensor broke!)

  ---

  get_reading(self):
    Purpose: The main method everything else will call.
              "Give me one validated sensor reading."
    
    Steps:
      1. Call read_raw_line() → get raw_line
      2. If raw_line is None, return None
      3. Call parse_line(raw_line) → get parsed
      4. Call validate_reading(parsed) → get validated
      5. If validated is not None:
         - Store it: self.last_reading = validated
      6. Return validated

  ---

  close(self):
    - Call self.serial.close()
    - Print: "📡 Serial reader closed"

---

MAIN BLOCK (if __name__ == "__main__"):
Purpose: Test serial_reader.py standalone

Steps:
  1. Create a SerialReader (use_simulator=True)
  2. Print: "Reading sensor data — press Ctrl+C to stop"
  3. Loop forever:
     - Call get_reading()
     - If reading is not None:
         Print the status and values in a nice format, for example:
         f"[{reading['timestamp']}] Status: {reading['status']}"
         f"  🌡️  Temp: {reading['temperature']}°C"
         f"  💧 Humidity: {reading['humidity']}%"
         f"  💨 Air Quality: {reading['air_quality']} ppm"
         f"  🌧️  Rain: {'Yes' if reading['rain'] == 1 else 'No'}"
         f"  🌬️  Pressure: {reading['pressure']} hPa"
         Print a blank line between readings for readability
  4. Handle KeyboardInterrupt:
     - Call close()
     - Print: "Stopped."
```

---

#### Step 3 — Update `main.py`

Now let's connect everything in the root `main.py`. This is the file you'll always run to start Luna.

```
PSEUDOCODE for main.py:

--- IMPORTS ---
Import SerialReader from python.serial_reader
  (Note: since main.py is in the root folder, 
   the import path is "python.serial_reader")

--- MAIN FUNCTION ---
def main():
  Print a welcome banner, something like:
  "🌱 Luna — AI Plant Care System"
  "================================"
  
  Create a SerialReader (use_simulator=True)
  
  Try:
    Loop forever:
      Call reader.get_reading()
      If reading is not None:
        Print: f"✅ Reading received: {reading['temperature']}°C, {reading['humidity']}% RH"
  
  Except KeyboardInterrupt:
    reader.close()
    Print: "👋 Luna is going to sleep. Goodbye!"

--- RUN ---
if __name__ == "__main__":
    main()
```

---

#### Step 4 — Run and Test

Test each file separately first, then together.

**Test serial_reader.py alone:**
```
uv run python python/serial_reader.py
```

You should see nicely formatted output like:
```
📡 Using simulated sensor data
🌱 Simulated serial port active on SIMULATED
Reading sensor data — press Ctrl+C to stop

[2026-04-30 21:30:00] Status: ok
  🌡️  Temp: 20.5°C
  💧 Humidity: 63.5%
  💨 Air Quality: 412 ppm
  🌧️  Rain: No
  🌬️  Pressure: 1013.20 hPa
```

**Then test main.py:**
```
uv run python main.py
```

You should see the welcome banner followed by reading confirmations.

---

### 📁 Files Modified in This Phase

| File | What Changed |
|------|-------------|
| `python/config.py` | Filled in — all settings in one place |
| `python/serial_reader.py` | Main new file — reads, parses, validates |
| `main.py` | First version — starts Luna and prints readings |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Importing `sensor_simulator` with wrong path | `ModuleNotFoundError` | If running from project root, import as `from python.sensor_simulator import SimulatedSerial` |
| Not handling `None` from `read_raw_line()` | Crashes when passing `None` to `parse_line()` | Always check `if raw_line is None: return None` |
| Using bare `except:` without catching what went wrong | Hides bugs silently | Use `except Exception as e:` and print `e` |
| Hardcoding `"SIMULATED"` in serial_reader.py | Not using your config | Import `SERIAL_PORT` from config |
| Forgetting to convert types after parsing | `"24.5"` is a string, not a number | Always use `float()` and `int()` |
| Putting validation logic inside `parse_line()` | Mixes two responsibilities | Keep parsing and validation in separate methods |

---

### 💡 Important Note About the Import Path

Since your `main.py` is in the **root folder** and `serial_reader.py` is in the **`python/` subfolder**, the import in `main.py` should be:

```python
from python.serial_reader import SerialReader
```

But when you run `serial_reader.py` **directly** (as a standalone test), it imports `SimulatedSerial` from the same folder:

```python
from sensor_simulator import SimulatedSerial  # runs from python/ folder
```

This can cause a conflict. Here's the clean solution — at the top of `serial_reader.py`, use this pattern:

```
PSEUDOCODE:
Try:
    from python.sensor_simulator import SimulatedSerial   # when called from root
Except ImportError:
    from sensor_simulator import SimulatedSerial          # when run directly
```

This makes your file work **both** when run directly AND when imported from main.py.

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/serial_reader.py` shows formatted sensor readings every 2 seconds
- [ ] Each reading shows: timestamp, status "ok", and all 5 sensor values
- [ ] `uv run python main.py` shows the welcome banner and brief reading confirmations
- [ ] Pressing Ctrl+C exits cleanly with a goodbye message in both files
- [ ] `config.py` has thresholds defined — try setting `TEMP_MAX = 10` temporarily and see if status changes to "error" (then change it back!)

---

### 🎊 Phase 3 Celebration (when you're done!)

You've built the **nervous system of Luna's body**! 🧠

Think about what you've actually created:
- A configurable settings hub (`config.py`)
- A professional data pipeline: raw bytes → parsed dict → validated dict
- Error handling that won't crash when something unexpected happens  
- Clean separation of concerns across three files
- A `main.py` that's the single entry point for the whole system

Every professional data pipeline in the world follows exactly this pattern: **ingest → parse → validate → forward**. You just built one from scratch.

---

## ⏸️ STOP HERE

> 👉 Build `config.py`, `serial_reader.py`, and update `main.py`
>
> Test them, see the readings flow cleanly
>
> When you're done, type: **"Phase 3 done"** or **"Next"**
>
> I'll then give you **Phase 4: Luna's AI Brain with Gemini** 🧠✨

---

## 📊 Where We Are in the Project

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  🔨 You are here — Serial bridge
Phase 4  ⏳ AI Brain (Gemini API)
Phase 5  ⏳ Luna's Voice (Vosk + Piper)
Phase 6  ⏳ Memory & Data
Phase 7  ⏳ Health Scoring
Phase 8  ⏳ Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **30% done** with the whole project. Keep going — you're doing great! 🌿

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 3 of 10*
