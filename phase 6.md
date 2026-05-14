# 🌱 Luna — Phase 6: Memory & Data
### Teaching Luna to Remember 🧠💾

> **Remember**: Read the pseudocode, understand every line, then write Python yourself. Luna's memory is what makes her feel truly alive!

---

## 🎉 Phase 5 Check — Here's What I Found

| Check | Status | Note |
|-------|--------|------|
| `PiperTTS` class structure | ✅ | `available` flag, graceful fallback, correct |
| `--output-raw` flag in subprocess | ✅ | Correct — raw PCM bytes |
| `rate=22050` for PyAudio playback | ✅ | Matches Piper output — correct |
| `VoskSTT` class | ✅ | Model loading, KaldiRecognizer, loop all correct |
| `AUDIO_SAMPLE_RATE=16000` for recording | ✅ | Correct — Vosk needs 16000 Hz |
| `finally:` block closes audio stream | ✅ | Great defensive coding! |
| `LunaVoice` wrapper | ✅ | Clean, simple |
| `speak_response()` method | ✅ | Sensible speech text building |
| `__main__` test block | 🔧 Added | Was missing — now you can test standalone |
| Hardcoded absolute path in config.py | 🔧 Fixed | Now uses `os.path.join(_project_root, ...)` — portable! |
| Piper producing no output | 🔧 Diagnosed | **Missing DLL files** — see fix below |
| `main.py` voice integration | ✅ | `voice.speak_response(response)` in the loop |

---

## ⚠️ ACTION REQUIRED: Fix Piper Before Continuing

Your `piper/` folder only contains `piper.exe` (509 KB). **This is too small** — the real Piper needs several DLL files to work.

**Do this now:**
1. Go to 👉 https://github.com/rhasspy/piper/releases/latest
2. Download `piper_windows_amd64.zip` (should be ~30–50 MB)
3. Extract the **entire zip** into your `piper/` folder

After extraction, `piper/` should contain:
```
piper/
├── piper.exe
├── espeak-ng-data/        ← folder (required)
├── libespeak-ng.dll       ← required
├── libonnxruntime.dll     ← required
└── piper_phonemize.dll    ← required (or similar)
```

Then test with this exact command (note: no `echo`, pipe directly):
```powershell
"Hello I am Luna" | .\piper\piper.exe --model voice\piper_voices\en_US-lessac-medium.onnx --output_file test_output.wav
```

Then open `test_output.wav` in Windows Media Player — you should hear Luna's voice!

---

## ✅ Phase 6 — Luna's Memory System

> **Stop after this phase and tell me "Phase 6 done" when finished!**

---

### 🎯 Goal

Build `python/memory.py` — Luna's long-term memory.

Right now, Luna reads sensor data, analyses it, and then... forgets it completely. Every cycle is fresh. That's like a doctor who never keeps patient records — each visit starts from zero.

By the end of Phase 6, Luna will:
- Remember the last 100 sensor readings (rolling buffer)
- Remember the last 20 AI responses
- Calculate daily averages (average temp, humidity, AQI per day)
- Detect trends ("temperature has been rising for the last hour")
- Save everything to disk so memory **survives restarts**

---

### 🤔 Why Does Luna Need Memory?

Memory unlocks the most powerful features of the whole system:

| Without Memory | With Memory |
|---------------|-------------|
| "It's 28°C right now" | "It's been above 26°C for 6 hours — heat stress is building" |
| "Humidity is 30%" | "Humidity dropped 20% in the last 2 hours — drought pattern" |
| Every AI call is context-free | AI can say "this is worse than yesterday" |
| No trend detection | "Your plant is getting sicker, not better" |

Memory is also what allows Phase 7 (Health Scoring) and Phase 8 (Daily Care Plans) to be meaningful — they both rely on historical data.

---

### 🧠 Three Concepts to Understand First

#### 1. JSON as a Database
For this project, we use a simple JSON file as our "database." It's not as powerful as a real database (like SQLite), but it's:
- Human-readable — you can open it in VS Code and see the data
- No setup required — just read/write a file
- Perfect for the amount of data we're storing

The memory file will look like:
```json
{
  "readings": [...],
  "ai_responses": [...],
  "daily_summaries": {...}
}
```

#### 2. Rolling Buffer (Deque)
A **rolling buffer** keeps only the last N items. When it's full and you add a new item, the oldest one is automatically dropped.

Python has a built-in `collections.deque` with `maxlen` for exactly this:
```python
from collections import deque
buffer = deque(maxlen=5)
for i in range(7):
    buffer.append(i)
# buffer is now: [2, 3, 4, 5, 6] — first two were dropped
```

We'll use this to keep the last 100 readings without ever running out of memory.

#### 3. Trend Detection
A "trend" is a direction of change over time. We can detect it simply:
1. Take the last N readings of a value (e.g., temperature)
2. Compare the average of the **first half** to the **second half**
3. If second > first by more than a threshold → "rising"
4. If second < first by more than a threshold → "falling"
5. Otherwise → "stable"

This is called a **simple moving average comparison** — no fancy maths required!

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py`

Add these new settings at the bottom:

```
PSEUDOCODE — add to config.py:

MAX_READINGS_IN_MEMORY = 100    # Keep last 100 sensor readings
MAX_AI_RESPONSES_IN_MEMORY = 20 # Keep last 20 AI responses
TREND_WINDOW = 10               # Use last 10 readings for trend detection
```

---

#### Step 2 — Build `python/memory.py`

```
PSEUDOCODE for memory.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: os, json, sys
Import: datetime from datetime
Import: deque from collections
Add UTF-8 fix (same pattern as other files)

Try dual-import:
    from python.config import MEMORY_FILE_PATH, MAX_READINGS_IN_MEMORY, 
                              MAX_AI_RESPONSES_IN_MEMORY, TREND_WINDOW
    Except ImportError: from config import ...

--- CLASS: LunaMemory ---

  __init__(self):
    Set self.readings = deque(maxlen=MAX_READINGS_IN_MEMORY)
    Set self.ai_responses = deque(maxlen=MAX_AI_RESPONSES_IN_MEMORY)
    Set self.daily_summaries = {}    ← regular dict, keyed by date string "2026-05-10"
    
    Call self._load()   ← load saved memory from disk
    
    Print: "💾 Memory system ready"

  ---

  _load(self):
    Purpose: Load saved data from luna_memory.json on startup
    
    If the file doesn't exist yet, just return (nothing to load)
    Check with: os.path.isfile(MEMORY_FILE_PATH)
    
    Try:
      Open the file in read mode ("r", encoding="utf-8")
      Parse it: data = json.load(file)
      
      Load readings:
        For each item in data.get("readings", []):
          self.readings.append(item)
      
      Load ai_responses:
        For each item in data.get("ai_responses", []):
          self.ai_responses.append(item)
      
      Load daily_summaries:
        self.daily_summaries = data.get("daily_summaries", {})
      
      Print: f"💾 Loaded {len(self.readings)} readings from memory"
    
    Except Exception as error:
      Print: f"⚠️ Could not load memory: {error}"

  ---

  _save(self):
    Purpose: Save current memory to luna_memory.json
    
    Make sure the folder exists:
      os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)
    
    Build a dict to save:
      data = {
          "readings": list(self.readings),        ← convert deque to list for JSON
          "ai_responses": list(self.ai_responses),
          "daily_summaries": self.daily_summaries,
          "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      }
    
    Write to file:
      Open MEMORY_FILE_PATH in write mode ("w", encoding="utf-8")
      json.dump(data, file, indent=2)
      ← indent=2 makes it human-readable with nice formatting

  ---

  add_reading(self, reading):
    Purpose: Store a new sensor reading in memory
    
    If reading is None: return
    
    self.readings.append(reading)
    
    Also update daily summary for today:
      today = datetime.now().strftime("%Y-%m-%d")
      self._update_daily_summary(today, reading)
    
    Save to disk:
      self._save()

  ---

  add_ai_response(self, response):
    Purpose: Store a new AI response in memory
    
    If response is None: return
    
    Add a timestamp to the response (if it doesn't have one):
      response_with_time = response.copy()    ← make a copy, don't mutate original
      response_with_time["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    self.ai_responses.append(response_with_time)
    self._save()

  ---

  _update_daily_summary(self, date_str, reading):
    Purpose: Update the running averages for a given day
    
    If date_str not in self.daily_summaries:
      Create a new entry:
        self.daily_summaries[date_str] = {
            "count": 0,
            "temp_sum": 0.0,
            "hum_sum": 0.0,
            "aqi_sum": 0,
            "rain_count": 0,
            "date": date_str
        }
    
    Get the existing entry:
      day = self.daily_summaries[date_str]
    
    Update it:
      day["count"] += 1
      day["temp_sum"] += reading["temperature"]
      day["hum_sum"] += reading["humidity"]
      day["aqi_sum"] += reading["air_quality"]
      day["rain_count"] += reading["rain"]

  ---

  get_daily_summary(self, date_str=None):
    Purpose: Get calculated averages for a given day
    
    If date_str is None:
      Use today: date_str = datetime.now().strftime("%Y-%m-%d")
    
    If date_str not in self.daily_summaries:
      Return None
    
    day = self.daily_summaries[date_str]
    count = day["count"]
    
    If count == 0:
      Return None
    
    Calculate and return averages:
      return {
          "date": date_str,
          "reading_count": count,
          "avg_temperature": round(day["temp_sum"] / count, 1),
          "avg_humidity": round(day["hum_sum"] / count, 1),
          "avg_air_quality": round(day["aqi_sum"] / count),
          "rain_events": day["rain_count"]
      }

  ---

  get_recent_readings(self, n=10):
    Purpose: Return the last n readings as a list
    
    Convert deque to list, then return last n items:
      all_readings = list(self.readings)
      return all_readings[-n:]   ← Python slice: last n items

  ---

  get_trend(self, field="temperature"):
    Purpose: Detect if a field is rising, falling, or stable
    
    Allowed fields: "temperature", "humidity", "air_quality", "pressure"
    
    Get the last TREND_WINDOW readings:
      recent = get_recent_readings(TREND_WINDOW)
    
    If len(recent) < 4:
      Return "insufficient data"   ← need at least 4 readings for a meaningful trend
    
    Split into two halves:
      mid = len(recent) // 2
      first_half = recent[:mid]
      second_half = recent[mid:]
    
    Calculate average of each half:
      avg_first = sum of field values in first_half / len(first_half)
      avg_second = sum of field values in second_half / len(second_half)
    
    Compare:
      difference = avg_second - avg_first
      
      If difference > 1.0:   ← more than 1 unit higher
        return "rising"
      Elif difference < -1.0:  ← more than 1 unit lower
        return "falling"
      Else:
        return "stable"

  ---

  get_summary_text(self):
    Purpose: Generate a human-readable summary of current memory state
    
    recent = get_recent_readings(5)
    
    If not recent:
      return "No readings in memory yet."
    
    last = recent[-1]   ← most recent reading
    temp_trend = get_trend("temperature")
    hum_trend = get_trend("humidity")
    
    today_summary = get_daily_summary()
    
    Build and return a formatted string:
      "📊 Luna Memory Summary:
       Latest: {last['temperature']}°C, {last['humidity']}% RH
       Temperature trend: {temp_trend}
       Humidity trend: {hum_trend}
       Readings in memory: {len(self.readings)}
       
       Today's averages ({today's date}):
         Avg temp: {today_summary['avg_temperature']}°C
         Avg humidity: {today_summary['avg_humidity']}%
         Rain events: {today_summary['rain_events']}"
    
    If today_summary is None, just omit the today section.

--- MAIN BLOCK (if __name__ == "__main__") ---
Purpose: Test memory standalone

Steps:
  1. Create LunaMemory instance
  2. Print: "Testing memory system..."
  
  # Feed 15 fake readings with gradually increasing temperature
  3. For i in range(15):
       Create a fake reading dict:
         timestamp = current time
         temperature = 22.0 + (i * 0.3)    ← slowly rising from 22 to 26.2
         humidity = 65.0 - (i * 0.5)       ← slowly falling
         air_quality = 420 + (i * 5)
         rain = 0
         pressure = 1013.0
         status = "ok"
       
       Call memory.add_reading(fake_reading)
       Print: f"Added reading {i+1}: Temp={temperature}"
  
  4. Print a blank line
  5. Print memory.get_summary_text()
  
  6. Print: "\nTrends:"
     Print: f"  Temperature: {memory.get_trend('temperature')}"
     Print: f"  Humidity: {memory.get_trend('humidity')}"
  
  7. Print: "\nToday's summary:"
     Print: memory.get_daily_summary()
  
  8. Print: "\n✅ Memory test complete! Check data/luna_memory.json"
```

---

#### Step 3 — Update `main.py`

Connect memory to the main loop:

```
PSEUDOCODE — additions to main.py:

--- NEW IMPORTS (add to existing imports) ---
from python.memory import LunaMemory

--- IN main() FUNCTION ---
After creating voice, also create:
  memory = LunaMemory()

In the reading loop, after checking reading is not None:
  # Store every reading in memory
  memory.add_reading(reading)

In the AI response section, after getting response:
  if response is not None:
    # Store the AI response in memory
    memory.add_ai_response(response)
    
    # Print trend info every 5th reading
    if reading_count % 5 == 0:
        print(memory.get_summary_text())
    
    print(brain.format_response(response))
    voice.speak_response(response)
    last_ai_call_time = current_time
```

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/memory.py` | New — full memory system |
| `python/config.py` | Added 3 new memory settings |
| `main.py` | Memory stores every reading + AI response |
| `data/luna_memory.json` | Auto-created when memory first saves |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Using a list instead of `deque` | List grows forever — memory leak | Use `deque(maxlen=N)` |
| Saving to disk on every single reading | Slow — file I/O 30x per minute | Still do save on every reading (file is small), but know this is a trade-off |
| Not converting `deque` to `list` before `json.dump()` | `json` can't serialise a deque | Always do `list(self.readings)` |
| Mutating the response dict before appending | Changes the original dict in the brain | Use `response.copy()` first |
| Not handling `os.makedirs` | Crashes if `data/` folder doesn't exist | Use `exist_ok=True` |
| Dividing by zero in trend calculation | If `recent` is empty | Always check `len(recent) >= 4` first |

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/memory.py` runs and prints the summary
- [ ] `data/luna_memory.json` is created and contains readable JSON
- [ ] The trend shows "rising" for temperature (we made it rise in the test)
- [ ] The trend shows "falling" for humidity (we made it fall in the test)
- [ ] Running the test twice loads the previous data ("Loaded X readings from memory")
- [ ] `uv run python main.py` — after a few readings, the summary appears every 5 cycles

---

### 🎊 Phase 6 Celebration (when you're done!)

💾 **Luna can remember now!**

You've built a persistent, rolling memory system with:
- Automatic disk persistence (survives restarts!)
- Rolling buffers that don't grow unbounded
- Daily aggregation statistics
- Real-time trend detection
- Human-readable summaries

This is the foundation of everything else. Phase 7's health scoring will use memory to detect sustained stress. Phase 8's care plans will use daily summaries. You've just built Luna's hippocampus! 🧠

---

## ⏸️ STOP HERE

> 👉 Fix Piper first (download full zip with DLLs)
>
> Then build `memory.py`, update `config.py` and `main.py`
>
> When you're done, type: **"Phase 6 done"** or **"Next"**
>
> I'll then give you **Phase 7: Health Scoring** 🩺

---

## 📊 Project Progress

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  ✅ Serial bridge — data pipeline
Phase 4  ✅ AI Brain — Luna thinks
Phase 5  ✅ Luna's Voice — speaks & listens
Phase 6  🔨 You are here — Memory & Data
Phase 7  ⏳ Health Scoring
Phase 8  ⏳ Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **60% done** 🌿 The hardest architecture is behind you!

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 6 of 10*