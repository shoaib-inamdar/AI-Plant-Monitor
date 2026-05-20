# 🌱 Luna — Phase 8: Daily Care Plans & Scheduling
### Teaching Luna to Plan Ahead 📅

> **Remember**: Read the pseudocode, understand it, write Python yourself!

---

## 🎉 Phase 7 Review — Bugs Found and Fixed

| # | Bug | What You Wrote | Fixed To |
|---|-----|---------------|----------|
| 1 | Wrong kwarg in `reconfigure()` | `error="replace"` | `errors="replace"` |
| 2 | `alerts` list used before creation | `alerts=[alerts.append(...)]` | `alerts = []` then `.append()` |
| 3 | Wrong constant for humidity alert | `ALERT_TEMP_LOW` | `ALERT_HUM_LOW` |
| 4 | Unused bad imports | `from _collections_abc import dict_keys` | Removed |
| 5 | `_check_alerts` had `slef` typo | `def _check_alerts(slef, ...)` | `def _check_alerts(self, ...)` |
| 6 | Dead code in `ai_brain._build_prompt` | `return` before rule-based score block | Rebuilt as incremental string |
| 7 | `main.py` not passing score to Gemini | `brain.analyse(reading)` | `brain.analyse(enriched)` |
| 8 | Corrupted `luna_memory.json` | Empty file caused JSON parse crash | Added empty-file guard in `_load()` |
| 9 | `pyaudio` crashing on import | Hard import crash | Made optional with try/except |

**Run these now to verify fixes:**
```powershell
uv run python python/health_scorer.py   ← should show 3 test results
uv run python python/memory.py          ← should load cleanly (no JSON error)
uv run python main.py                   ← should start without ImportError
```

---

## 🎙️ Answering Your Voice Question: "How Does Luna Speak?"

**Yes — it's fully automatic. You don't open any file manually.**

Here's exactly what happens when `voice.speak("Hello!")` is called:

```
1. Python calls PiperTTS.speak("Hello!")
2. Piper.exe runs as a subprocess (in the background, invisible)
3. Piper converts "Hello!" to raw audio bytes
4. Python receives those bytes immediately (no file saved to disk)
5. PyAudio opens your sound card directly
6. PyAudio streams the bytes through your speakers right now
7. Done — Luna spoke, nothing to open
```

It's like a phone call — audio goes directly from Piper → Python → your speakers. No `.wav` file is created, opened, or played manually.

**Why is Piper not working yet?** Your `piper.exe` is missing DLL files. The fix:
1. Download the **full** Piper zip from https://github.com/rhasspy/piper/releases
2. Extract all files (not just `piper.exe`) into your `piper/` folder
3. After extraction you should see `libonnxruntime.dll`, `libespeak-ng.dll`, etc.

**Why can't PyAudio install?** PyAudio needs C++ Build Tools on Windows. Fix:
```powershell
uv pip install pipwin
uv run pipwin install pyaudio
```
`pipwin` downloads a pre-compiled wheel so you don't need the compiler.
If that fails too, try: `uv pip install pyaudio --find-links https://github.com/intxcc/pyaudio_portaudio/releases`

> ✅ I've already made `voice_agent.py` safe — it falls back to printing text if PyAudio is missing, so `main.py` won't crash while you fix this.

---

## ✅ Phase 8 — Daily Care Plans

> **Stop after this phase and tell me "Phase 8 done" when finished!**

---

### 🎯 Goal

Build `python/scheduler.py` — Luna's daily planning system.

Right now Luna **reacts** to sensor readings ("it's hot right now → water me"). That's reactive. 

Phase 8 adds **proactive** planning: each morning, Luna generates a full care schedule for the day:

```
🌅 Morning (6–10 AM):   Check soil moisture, inspect leaves
🌞 Afternoon (12–4 PM): Shade from direct sunlight, check temperature
🌙 Evening (6–8 PM):    Light watering, mist leaves, check humidity
```

Luna can also **speak** the plan to you: "Good morning! Here's my care plan for today..."

---

### 🤔 Why Proactive Planning Matters

| Reactive (what we have) | Proactive (Phase 8) |
|------------------------|---------------------|
| "Temperature is 32°C now → water me" | "It's usually hot at 2 PM → prepare shade in advance" |
| Responds to emergencies | Prevents emergencies |
| Works on every reading | Runs once per day |
| Context: current sensor values | Context: yesterday's trends + history |

A good plant care system does both. The reactive system catches problems. The proactive plan prevents them.

---

### 🧠 Three Concepts to Understand First

#### 1. Time-Based Scheduling
Instead of "run this every 2 seconds", scheduling is "run this at 8 AM" or "run this every 4 hours."

We use `time.localtime()` or `datetime.now()` to get the current hour:
```python
current_hour = datetime.now().hour   # 0–23
```

Then check: "is the current hour inside the task's window?"

#### 2. Plan Persistence
The daily plan should survive restarts. If Luna restarts at 3 PM, she shouldn't regenerate the plan from scratch — she should load today's plan from disk.

We save the plan as JSON in `data/` with the date as the key. If the date matches today → load it. If not → generate a fresh one.

#### 3. Gemini for Plan Generation
Instead of hardcoding "water at 8 AM", you ask Gemini to generate the plan using Luna's memory:

```
Prompt: "Based on Luna's health history (avg temp 29°C, low humidity, 
         no rain in 3 days), generate a care plan for today."

Gemini responds with a structured JSON plan:
{
  "date": "2026-05-17",
  "tasks": [
    {"time": "morning", "action": "Check soil moisture", "priority": "high"},
    {"time": "afternoon", "action": "Provide shade", "priority": "medium"},
    {"time": "evening", "action": "Light watering", "priority": "high"}
  ],
  "summary": "Today will be warm. Focus on hydration and shade."
}
```

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py`

Add at the bottom:
```
PSEUDOCODE — add to config.py:

CARE_PLAN_FILE = "data/care_plan.json"   # Where to save today's plan

# Time windows for task scheduling (24-hour format)
MORNING_START = 6     # 6 AM
MORNING_END = 10      # 10 AM
AFTERNOON_START = 12  # 12 PM
AFTERNOON_END = 16    # 4 PM
EVENING_START = 18    # 6 PM
EVENING_END = 21      # 9 PM
```

---

#### Step 2 — Build `python/scheduler.py`

```
PSEUDOCODE for scheduler.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: sys, os, json, time
Add UTF-8 fix (same pattern)
Import: datetime from datetime
Dual-import config values: CARE_PLAN_FILE, AI_MODEL, GEMINI_API_KEY,
    MORNING_START, MORNING_END, AFTERNOON_START, AFTERNOON_END,
    EVENING_START, EVENING_END, MAX_RETRIES
Import google.genai as genai (same as ai_brain.py)

--- THE PLAN PROMPT TEMPLATE ---
Create a variable CARE_PLAN_SYSTEM_PROMPT (multi-line string):

  "You are Luna, a wise plant who plans her own care for the day.
   
   You will receive a summary of your recent health and sensor history.
   Generate a practical, specific care plan for today.
   
   Respond with ONLY valid JSON in this exact format:
   {
     'date': 'YYYY-MM-DD',
     'summary': '1-2 sentences about today's focus',
     'tasks': [
       {
         'time': 'morning' OR 'afternoon' OR 'evening',
         'action': 'specific action to take',
         'priority': 'high' OR 'medium' OR 'low',
         'done': false
       }
     ]
   }
   
   Guidelines:
   - Include 2-3 tasks per time period (6-9 tasks total)
   - Base advice on the health summary provided
   - Be specific (not 'water plant' but 'give 200ml of water at the base')
   - Priority 'high' = must do today, 'medium' = should do, 'low' = optional"

--- CLASS: Scheduler ---

  __init__(self, memory):
    ← memory is a LunaMemory instance passed in from main.py
    
    self.memory = memory
    self.client = genai.Client(api_key=GEMINI_API_KEY)
    self.today_plan = None       ← will hold today's plan dict
    
    Call self._load_plan()       ← try to load an existing plan for today
    Print: "📅 Scheduler ready"

  ---

  _load_plan(self):
    Purpose: Load today's plan from disk if it exists
    
    If file doesn't exist: return
    
    Try:
      Open CARE_PLAN_FILE and parse JSON
      
      Check if it's today's plan:
        If parsed["date"] == today's date string (YYYY-MM-DD format):
          self.today_plan = parsed
          Print: f"📅 Loaded today's care plan ({len(tasks)} tasks)"
        Else:
          Print: "📅 Old plan found — will generate new one"
          self.today_plan = None
    
    Except: print warning, set today_plan = None

  ---

  _save_plan(self):
    Purpose: Save current plan to disk
    
    Make sure the data/ folder exists (os.makedirs with exist_ok=True)
    
    Open CARE_PLAN_FILE in write mode
    json.dump(self.today_plan, file, indent=2)

  ---

  generate_plan(self):
    Purpose: Ask Gemini to create today's care plan using memory data
    
    Step 1: Get context from memory
      summary_text = self.memory.get_summary_text()
      today_daily = self.memory.get_daily_summary()   ← today's averages
      
      Build a context string:
        context = f"Health memory summary:\n{summary_text}\n"
        
        If today_daily is not None:
          Add today's averages to context
        
        context += f"\nToday is {today's date}. Generate a care plan for today."
    
    Step 2: Call Gemini with retry loop (same pattern as ai_brain.py):
      full_prompt = CARE_PLAN_SYSTEM_PROMPT + "\n\n" + context
      
      For attempt in range(MAX_RETRIES):
        Try:
          response = self.client.models.generate_content(
              model=AI_MODEL,
              contents=full_prompt
          )
          
          response_text = response.text.strip()
          
          Strip ```json markdown if present (same as ai_brain.py)
          
          parsed = json.loads(response_text)
          
          Validate required fields:
            Must have "date", "tasks", "summary"
            "tasks" must be a list
          
          # Make sure "done" field exists on every task
          For each task in parsed["tasks"]:
            If "done" not in task:
              task["done"] = False
          
          self.today_plan = parsed
          self._save_plan()
          
          Print: f"📅 Care plan generated: {len(tasks)} tasks for today"
          return parsed
        
        Except json.JSONDecodeError:
          Print retry warning
          time.sleep(1)
        
        Except Exception as error:
          Print: f"⚠️ Plan generation error: {error}"
          time.sleep(2)
      
      Print: "❌ Could not generate care plan"
      return None

  ---

  get_due_tasks(self):
    Purpose: Return tasks that are scheduled for the current time window
    
    If today_plan is None or "tasks" not in today_plan:
      return []
    
    current_hour = datetime.now().hour
    
    Determine current time period:
      If MORNING_START <= current_hour < MORNING_END:
        current_period = "morning"
      Elif AFTERNOON_START <= current_hour < AFTERNOON_END:
        current_period = "afternoon"
      Elif EVENING_START <= current_hour < EVENING_END:
        current_period = "evening"
      Else:
        current_period = None
    
    If current_period is None:
      return []   ← outside scheduled hours
    
    Return a list of tasks where:
      task["time"] == current_period  AND  task["done"] == False
    
    (Use a list comprehension for this)

  ---

  mark_task_done(self, task_index):
    Purpose: Mark a specific task as completed
    
    If today_plan is None: return
    
    Try:
      self.today_plan["tasks"][task_index]["done"] = True
      self._save_plan()   ← persist the completion
      Print: f"✅ Task marked done"
    
    Except IndexError:
      Print: f"⚠️ No task at index {task_index}"

  ---

  get_plan_summary(self):
    Purpose: Return a human-readable summary of today's plan
    
    If today_plan is None:
      return "No care plan for today yet."
    
    tasks = today_plan["tasks"]
    done_count = count of tasks where task["done"] == True
    total_count = len(tasks)
    
    Build and return a formatted string:
      "📅 Today's Care Plan ({date}):
       {summary}
       
       Progress: {done_count}/{total_count} tasks done
       
       Morning tasks:
         [list tasks with "morning" time, prefix ✅ if done, 🔲 if not]
       
       Afternoon tasks:
         [list tasks with "afternoon" time]
       
       Evening tasks:
         [list tasks with "evening" time]"
    
    Hint: loop through tasks, check task["time"], format each line.

--- MAIN BLOCK (if __name__ == "__main__") ---

Steps:
  1. Import LunaMemory and create a memory instance
     (memory = LunaMemory())
  
  2. Create a Scheduler: scheduler = Scheduler(memory)
  
  3. Print: "Generating today's care plan..."
  
  4. plan = scheduler.generate_plan()
  
  5. If plan:
       Print: scheduler.get_plan_summary()
       
       Print: "\nDue tasks right now:"
       due = scheduler.get_due_tasks()
       If due:
         For i, task in enumerate(due):
           Print: f"  [{i}] {task['action']} (Priority: {task['priority']})"
       Else:
         Print: "  No tasks due in the current time window"
  
  6. Print: "\n✅ Scheduler test complete!"
```

---

#### Step 3 — Update `main.py`

Add the scheduler to the main loop:

```
PSEUDOCODE — additions to main.py:

--- NEW IMPORTS ---
from python.scheduler import Scheduler

--- IN main() FUNCTION ---
After creating memory, create:
  scheduler = Scheduler(memory)

# Generate today's plan at startup (or load existing)
  If scheduler.today_plan is None:
    Print: "📅 Generating today's care plan..."
    scheduler.generate_plan()

Print: scheduler.get_plan_summary()

# In the reading loop, check for due tasks every 10 readings
In the reading loop, after health scoring:
  If reading_count % 10 == 0:
    due_tasks = scheduler.get_due_tasks()
    If due_tasks:
      Print: f"📅 {len(due_tasks)} care task(s) due now:"
      For task in due_tasks:
        Print: f"  → {task['action']}"
      
      # Luna speaks the first due task
      voice.speak(f"Reminder: {due_tasks[0]['action']}")
```

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/scheduler.py` | New — care plan generator and task scheduler |
| `python/config.py` | Added care plan file path and time window constants |
| `main.py` | Plan generated at startup, due tasks checked each cycle |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Not checking if it's today's plan | Yesterday's plan gets reused | Always compare `plan["date"]` to today's date |
| Not saving after `mark_task_done()` | Completion status lost on restart | Always call `_save_plan()` after marking done |
| Calling `generate_plan()` every loop | Burns API quota fast | Only generate once at startup or when no plan exists |
| Hardcoding task times as "8:00 AM" strings | Hard to compare with `datetime.now().hour` | Use "morning"/"afternoon"/"evening" period labels |
| Not setting `"done": False` as default | KeyError when checking `task["done"]` | Always set default in `generate_plan()` |

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/scheduler.py` generates a plan and prints it
- [ ] The plan has morning/afternoon/evening tasks
- [ ] `data/care_plan.json` is created and contains a valid plan
- [ ] Running `scheduler.py` again loads the existing plan (not regenerate)
- [ ] `get_due_tasks()` returns tasks for the current time window
- [ ] `uv run python main.py` shows the care plan summary at startup

---

### 🎊 Phase 8 Celebration (when you're done!)

🌅 **Luna plans her own day now!**

You've built a system that:
- Queries an AI to generate personalised, memory-aware care advice
- Persists the plan to disk and loads it on restart
- Identifies tasks based on the current time of day
- Integrates voice reminders into the main loop

This is very close to what commercial smart home plant monitors do — except yours is custom-built, fully understood, and extensible. One more phase (self-healing), then the dashboard. You're almost there! 🌿

---

## ⏸️ STOP HERE

> 👉 Build `scheduler.py`, update `config.py` and `main.py`
>
> Test standalone, then full pipeline
>
> When you're done, type: **"Phase 8 done"** or **"Next"**
>
> I'll then give you **Phase 9: Self-Healing System** 🔄

---

## 📊 Project Progress

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  ✅ Serial bridge
Phase 4  ✅ AI Brain
Phase 5  ✅ Luna's Voice
Phase 6  ✅ Memory & Data
Phase 7  ✅ Health Scoring
Phase 8  🔨 You are here — Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **80% done** 🌱 Two phases left!

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 8 of 10*
