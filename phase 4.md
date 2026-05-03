# 🌱 Luna — Phase 4: Luna's AI Brain (Gemini API)
### Teaching Luna to Actually Think 🧠✨

> **Remember the rule**: Read the pseudocode carefully, understand it, then type the Python yourself. This is where the magic happens!

---

## 🎉 Phase 3 Check — You Passed!

Here's what was found and fixed:

| Check | Status | Note |
|-------|--------|------|
| `serial_reader.py` structure | ✅ | All methods correct |
| `parse_line()` logic | ✅ | String splitting and type conversion working |
| `validate_reading()` | ✅ | Threshold checks all correct |
| `get_reading()` pipeline | ✅ | Ingest → Parse → Validate → Return |
| `config.py` settings | ✅ | All thresholds and paths defined |
| `main.py` entry point | ✅ | Connects everything cleanly |
| Import error (`No module 'config'`) | 🔧 Fixed | Added try/except dual-import pattern |
| `load_dotenv()` path issue | 🔧 Fixed | Now uses `__file__` to find project root |
| Emoji crash on Windows | 🔧 Fixed | Added `sys.stdout.reconfigure(encoding="utf-8")` |
| Missing `python/__init__.py` | 🔧 Fixed | Created it — makes `python/` a proper package |

**One important thing**: When running `main.py`, always use:
```
$env:PYTHONUTF8="1"; uv run python main.py
```
Or permanently fix it by opening PowerShell and running once:
```
[System.Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```
Then restart PowerShell — after that you can just use `uv run python main.py` normally.

---

## ✅ Phase 4 — Luna's AI Brain (Gemini)

> **Stop after this phase and tell me "Phase 4 done" when finished!**

---

### 🎯 Goal

Build `python/ai_brain.py` — the file where Luna actually **thinks**.

You'll send sensor readings to Google Gemini and get back:
- A health assessment for the plant
- Specific care advice ("water me now!" or "I'm doing great!")
- A health score from 0–100
- An explanation of the AI's reasoning

By the end of this phase, Luna will respond to sensor data like a real personality. This is the moment the project becomes genuinely exciting! 🌿

---

### 🤔 Why This Phase Matters

Right now Luna can read data. But reading data isn't intelligence — it's just plumbing.

Intelligence is: "The temperature is 35°C, humidity is 18%, and it's been dry for 3 days... I need water urgently and I'm stressed."

That reasoning is what the Gemini API provides. You're essentially hiring a very smart consultant (Gemini) who reads Luna's sensor report and gives expert plant care advice — instantly, every time.

---

### 🧠 Four Concepts to Understand First

#### 1. What is a System Prompt?
When you call the Gemini API, you send two things:
- A **system prompt** — background instructions that define who Gemini "is" for this conversation
- A **user message** — the actual question or data you're sending

Think of the system prompt as a job description. You're telling Gemini:
> "You are Luna, a thoughtful plant who speaks with wisdom and gentle humour. You analyse sensor data and give care advice. Always respond in JSON format..."

The system prompt shapes every response Gemini gives. A well-written system prompt is the difference between generic AI output and Luna feeling like a real character.

#### 2. What is JSON in this context?
We'll ask Gemini to respond in **JSON format** — a structured text format that Python can easily parse.

Instead of free-form text:
> "I'm feeling a bit warm today and could use some water!"

We ask for:
```json
{
    "health_score": 62,
    "status": "mild_stress",
    "message": "I'm feeling a bit warm today and could use some water!",
    "actions": ["water now", "move to shade"],
    "reason": "Temperature is above optimal range and humidity is low"
}
```

The JSON format means your Python code can extract `health_score` as a number, `actions` as a list, etc. This is how AI becomes useful in a real system — not just chatting, but returning structured data you can act on.

#### 3. What are Tokens?
Gemini charges by "tokens" (chunks of text). Every word you send and receive costs tokens.

- Gemini 1.5 Flash has a **free tier** — you get ~1 million tokens per day for free
- One sensor reading call uses roughly 300–500 tokens
- At 1 reading every 30 seconds, that's about 86,400 tokens/day — well within free limits
- ⚠️ If you call it every 2 seconds, you'll hit limits fast. We'll call AI every 30 seconds, not every reading.

#### 4. What is `json.loads()`?
Gemini returns text. Even if we ask for JSON, it comes back as a **string**:
```
'{"health_score": 62, "status": "mild_stress", ...}'
```

`json.loads()` converts that string into a Python dictionary you can use:
```python
import json
response_text = '{"health_score": 62}'
data = json.loads(response_text)
print(data["health_score"])  # → 62
```

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py`

Add these two new settings to your `config.py` (at the bottom):

```
PSEUDOCODE — add to config.py:

AI_CALL_INTERVAL = 30    # Call Gemini every 30 seconds (not every reading!)
                         # This saves your free API tokens

MAX_RETRIES = 3          # How many times to retry if Gemini fails
```

---

#### Step 2 — Build `python/ai_brain.py`

This is the main file for Phase 4. Open it and write based on this structure:

```
PSEUDOCODE for ai_brain.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: os, json, time
Import google.generativeai as genai
Try to import config values (dual-import pattern like serial_reader.py):
    Try: from python.config import GEMINI_API_KEY, GROQ_API_KEY, AI_MODEL, USE_BACKUP_AI, MAX_RETRIES
    Except ImportError: from config import ...

--- SETUP GEMINI ---
After imports, configure the Gemini API:
    genai.configure(api_key=GEMINI_API_KEY)

--- THE SYSTEM PROMPT (this is Luna's personality!) ---
Create a variable called LUNA_SYSTEM_PROMPT.
This is a long multi-line string (use triple quotes: """ ... """).

Write it like this (in your own words, but include these ideas):
  "You are Luna, a wise and gentle plant who monitors her own environment.
   You speak in first person as the plant — warm, slightly poetic, but practical.
   You receive sensor readings and analyse your own health.
   
   You MUST always respond with valid JSON and nothing else. No explanations outside the JSON.
   
   Your JSON response must have exactly these fields:
   {
     "health_score": a number from 0 to 100 (100 = perfect health),
     "status": one of: "excellent", "good", "mild_stress", "stressed", "critical",
     "message": a 1-2 sentence message FROM Luna IN FIRST PERSON about how she feels,
     "actions": a list of 1-3 specific care actions needed (strings),
     "reason": a brief technical explanation of WHY you gave this score
   }
   
   Sensor ranges for reference:
   - Temperature: 18-26°C is ideal for most plants
   - Humidity: 50-70% is ideal
   - Air quality: below 600 ppm is good
   - Rain: 0 = no rain detected, 1 = rain detected
   - Pressure: 1000-1020 hPa is normal"

--- CLASS: LunaBrain ---

  __init__(self):
    Create the Gemini model:
      self.model = genai.GenerativeModel(
          model_name=AI_MODEL,
          system_instruction=LUNA_SYSTEM_PROMPT
      )
    Set self.last_response = None
    Print: "🧠 Luna's AI brain initialised"

  ---

  _build_prompt(self, reading):
    Purpose: Format the sensor reading as a clear message to send to Gemini
    
    reading is the dictionary from serial_reader.py:
    {"timestamp": ..., "temperature": ..., "humidity": ..., 
     "air_quality": ..., "rain": ..., "pressure": ..., "status": ...}
    
    Return a formatted string like:
    
    "Current sensor readings for Luna:
     Timestamp: {reading['timestamp']}
     Temperature: {reading['temperature']}°C
     Humidity: {reading['humidity']}%
     Air Quality: {reading['air_quality']} ppm
     Rain detected: {'Yes' if reading['rain'] == 1 else 'No'}
     Barometric Pressure: {reading['pressure']} hPa
     Sensor status: {reading['status']}
     
     Please analyse these readings and respond with your JSON assessment."

  ---

  analyse(self, reading):
    Purpose: Send a reading to Gemini and get Luna's response back
    
    This is the main method. Everything else supports this one.
    
    Steps:
      1. If reading is None, return None
      
      2. Build the prompt: prompt = self._build_prompt(reading)
      
      3. Try up to MAX_RETRIES times:
         For attempt in range(MAX_RETRIES):
           Try:
             a. Call Gemini:
                response = self.model.generate_content(prompt)
             
             b. Get the text from the response:
                response_text = response.text.strip()
             
             c. Clean the response text:
                Sometimes Gemini wraps JSON in markdown like ```json ... ```
                Remove these if present:
                  If response_text starts with "```":
                    Remove the first line (```json)
                    Remove the last line (```)
                    Strip again
             
             d. Parse the JSON:
                parsed = json.loads(response_text)
             
             e. Validate the required fields exist:
                required = ["health_score", "status", "message", "actions", "reason"]
                For each field in required:
                  If field not in parsed:
                    raise ValueError(f"Missing field: {field}")
             
             f. Store and return:
                self.last_response = parsed
                return parsed
           
           Except json.JSONDecodeError:
             Print: f"⚠️ Attempt {attempt+1}: Gemini returned invalid JSON. Retrying..."
             time.sleep(1)
           
           Except Exception as error:
             Print: f"⚠️ Attempt {attempt+1}: API error — {error}"
             time.sleep(2)
      
      4. After all retries exhausted, return a safe fallback:
         Print: "❌ All retries failed. Using fallback response."
         return {
             "health_score": 50,
             "status": "unknown",
             "message": "I'm having trouble thinking right now. Please check my connections.",
             "actions": ["check system", "retry later"],
             "reason": "AI brain temporarily unavailable"
         }

  ---

  explain_decision(self):
    Purpose: Explainable AI — "Why did you say that?"
    
    If self.last_response is None:
      return "I haven't analysed any readings yet."
    
    Build and return a human-readable explanation string:
    
    "🌿 Luna's Last Assessment:
     Health Score: {last_response['health_score']}/100
     Status: {last_response['status'].upper()}
     
     What Luna said: {last_response['message']}
     
     Why: {last_response['reason']}
     
     Recommended actions:
     {for each action, print '  → {action}'}"

  ---

  format_response(self, response):
    Purpose: Pretty-print a response for the terminal
    
    If response is None: return "No response"
    
    Return a formatted string showing:
    - Health score with a visual bar or emoji (e.g., 🟢 for >70, 🟡 for 40-70, 🔴 for <40)
    - Status
    - Luna's message (in quotes)
    - Actions as a bullet list

--- MAIN BLOCK (if __name__ == "__main__") ---
Purpose: Test ai_brain.py standalone with fake data

Steps:
  1. Create a fake reading dictionary (hardcode some values):
     fake_reading = {
         "timestamp": "2026-05-01 10:00:00",
         "temperature": 32.0,     ← deliberately high to test stress response
         "humidity": 22.0,        ← deliberately low
         "air_quality": 650,
         "rain": 0,
         "pressure": 1010.50,
         "status": "ok"
     }
  
  2. Create a LunaBrain instance
  
  3. Print: "Sending reading to Luna's AI brain..."
  
  4. Call: response = brain.analyse(fake_reading)
  
  5. Print the formatted response using format_response()
  
  6. Print a blank line
  
  7. Print the explanation using explain_decision()
```

---

#### Step 3 — Update `main.py` to Include the AI Brain

Now connect the AI brain to the sensor pipeline. Update your `main.py`:

```
PSEUDOCODE — updated main.py:

--- IMPORTS (add to existing) ---
Import LunaBrain from python.ai_brain (using dual-import pattern)
Import time

--- MAIN FUNCTION (update) ---
def main():
  Print welcome banner
  
  reader = SerialReader(use_simulator=True)
  brain = LunaBrain()
  
  Print: "🌱 Luna is awake and listening to her senses..."
  
  reading_count = 0          ← count how many readings we've taken
  last_ai_call_time = 0      ← track when we last called Gemini
  
  Try:
    While True:
      reading = reader.get_reading()
      reading_count += 1
      
      If reading is not None:
        Print: f"📡 Reading #{reading_count}: Temp={reading['temperature']}°C, Hum={reading['humidity']}%"
        
        # Only call Gemini every AI_CALL_INTERVAL seconds
        current_time = time.time()
        time_since_last_call = current_time - last_ai_call_time
        
        If time_since_last_call >= AI_CALL_INTERVAL (import this from config):
          Print: "🧠 Asking Luna what she thinks..."
          response = brain.analyse(reading)
          
          If response is not None:
            Print the formatted response
            last_ai_call_time = current_time
      
      Else:
        Print: "⚠️ No reading this cycle"
  
  Except KeyboardInterrupt:
    reader.close()
    Print: "👋 Luna is going to sleep. Goodbye!"
```

---

#### Step 4 — Test It!

**Test the AI brain alone first:**
```
uv run python python/ai_brain.py
```

You should see Luna's response to the fake stressed reading. Something like:
```
🧠 Luna's AI brain initialised
Sending reading to Luna's AI brain...

🔴 Health Score: 38/100 | Status: STRESSED
💬 Luna says: "I'm really struggling today — it's so hot and dry. 
               I desperately need water and some shade!"
📋 Actions needed:
  → water immediately
  → move to cooler location
  → increase humidity

🌿 Luna's Last Assessment:
Health Score: 38/100
Status: STRESSED

Why: Temperature at 32°C exceeds optimal range (18-26°C) by 6 degrees.
     Humidity at 22% is critically below the 50-70% ideal range.
```

**Then test the full system:**
```
uv run python main.py
```

For the first 30 seconds, you'll see sensor readings. After 30 seconds, Luna will speak! 🌿

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/ai_brain.py` | New — the entire AI brain |
| `python/config.py` | Added `AI_CALL_INTERVAL` and `MAX_RETRIES` |
| `main.py` | Connected AI brain to sensor pipeline |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Calling Gemini on every reading (every 2s) | Hits API rate limits fast, wastes free quota | Only call every 30 seconds using `time.time()` |
| Not stripping the ```json``` markdown wrapper | `json.loads()` crashes on ` ```json` prefix | Check and strip before parsing |
| Not validating required JSON fields | Code crashes later when accessing missing keys | Check all required fields after parsing |
| Putting the API key directly in ai_brain.py | Security risk | Always use `GEMINI_API_KEY` from config |
| Using `model.generate_content()` inside a loop without try/except | One network error crashes everything | Always wrap API calls in try/except with retry |
| Not having a fallback response | If Gemini is down, whole program stops | Always return a safe default dict after retries |

---

### 💡 Gemini API Tips

**Free tier limits for Gemini 1.5 Flash:**
- 15 requests per minute (RPM)
- 1 million tokens per day
- At 1 call per 30 seconds = 2 calls/minute → well within limits ✅

**If you get a quota error:**
- Wait 60 seconds and try again
- Or temporarily set `USE_BACKUP_AI = True` in config to switch to Groq

**To switch to Groq as backup:**
In `ai_brain.py`, after the Gemini model is set up, add an if/else:
```
If USE_BACKUP_AI is True:
    Use Groq's API instead (we'll set this up in Phase 9 self-healing)
```
For now, just keep `USE_BACKUP_AI = False` and use Gemini.

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/ai_brain.py` works and prints a structured response
- [ ] Luna's health score changes based on the sensor values
- [ ] The status is one of: excellent / good / mild_stress / stressed / critical
- [ ] Luna speaks in first person in the message field
- [ ] `uv run python main.py` shows sensor readings AND (after 30 seconds) Luna's assessment
- [ ] If you change the fake_reading temperature to 20.0°C and humidity to 60%, the health score goes up

---

### 🎊 Phase 4 Celebration (when you're done!)

🌟 **Luna can think now.** 

You've integrated a real large language model into a hardware sensor pipeline. That's not beginner work — that's production-level IoT + AI engineering. You now have:

- A sensor data pipeline (Phases 2–3)
- An AI reasoning layer (Phase 4)
- A plant persona with structured JSON output
- Explainable AI ("why did you say that?")
- Rate limiting and retry logic
- Fallback safety

This is the point where most people stop because it feels like magic. But you understand exactly how it works — every line of code! 🌿

---

## ⏸️ STOP HERE

> 👉 Build `ai_brain.py`, update `config.py` and `main.py`
>
> Test the AI brain standalone, then test the full pipeline
>
> When you're done, type: **"Phase 4 done"** or **"Next"**
>
> I'll then give you **Phase 5: Luna's Voice (Vosk + Piper)** 🎙️

---

## 📊 Project Progress

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  ✅ Serial bridge — data pipeline working
Phase 4  🔨 You are here — AI Brain
Phase 5  ⏳ Luna's Voice (Vosk + Piper)
Phase 6  ⏳ Memory & Data
Phase 7  ⏳ Health Scoring
Phase 8  ⏳ Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **40% done** with the full project. The hard plumbing is behind you — from here it gets fun! 🌱

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 4 of 10*
