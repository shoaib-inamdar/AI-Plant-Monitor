# 🌱 Luna — Phase 9: Self-Healing System
### Teaching Luna to Fix Herself 🔄

> **Remember**: Read the pseudocode, understand the logic, write Python yourself!

---

## 🎉 Phase 8 Review — Bugs Fixed (11 Found!)

| # | Bug | Root Cause |
|---|-----|-----------|
| 1 | `try` without colon → SyntaxError | Missing `:` at end of `try` line |
| 2 | `json(file)` → TypeError | `json` is a module, not callable. Should be `json.load(file)` |
| 3 | `tasks` undefined in print | Used `tasks` before it was defined — should use `parsed["tasks"]` |
| 4 | `os.makedirs()` in `if` condition | `makedirs()` returns `None` — condition was always False, file never saved |
| 5 | `today_date` undefined in context | Variable was used but never assigned |
| 6 | `generate_cotent` typo | Missing letter → `AttributeError` |
| 7 | Positional `AI_MODEL` arg | Should be keyword: `model=AI_MODEL` |
| 8 | `response.summary_text` → `response.text` | `summary_text` is not an attribute of the Gemini response |
| 9 | Single quotes in JSON template | Invalid JSON in the prompt — Gemini got confused |
| 10 | `get_due_tasks` returned done tasks | Condition was `task.get("done", False)` — should be `not task.get(...)` |
| 11 | `get_plan_summary()` body was empty | The method existed but had no code inside |

> 💡 **The big lessons today**: Never use a function's return value in an `if` without checking what it returns. `os.makedirs()` always returns `None`. And when you name a method but don't write its body — Python accepts it silently, but calling it returns `None`.

---

**Scheduler output was excellent:**
```
📅 Today's Care Plan (2026-05-19):
   Progress: 0/9 tasks done
🌅 Morning: 3 specific tasks (mist, soil check, leaf inspection)
🌞 Afternoon: 3 tasks (humidity check, watering, rotation)
🌙 Evening: 3 tasks (dry leaves, airflow, reflection)
```

Luna is now planning her own day! 🌿

---

## ✅ Phase 9 — Self-Healing System

> **Stop after this phase and tell me "Phase 9 done" when finished!**

---

### 🎯 Goal

Build `python/healer.py` — Luna's self-healing brain.

Right now, if Luna's health is poor for 20 consecutive readings, **nothing special happens** — she just keeps reporting the same stressed score. There's no escalation.

Phase 9 adds an **escalation and recovery system**:
1. If health score is poor for N readings in a row → trigger healing protocol
2. Generate targeted recovery actions via Gemini (based on what's wrong)
3. Track whether each action has been attempted
4. Alert via voice for urgent situations
5. Reset and celebrate when health recovers

This is the difference between a **sensor** and a **care system**.

---

### 🤔 Why Self-Healing Matters

| Without Self-Healing | With Self-Healing |
|---------------------|------------------|
| Reports "stressed" every reading | Escalates after 5 minutes of stress |
| Same alert repeatedly | New targeted recovery plan each incident |
| User has to notice | Luna actively asks for help |
| No history of incidents | Tracks each healing attempt |

---

### 🧠 Three Concepts to Understand First

#### 1. State Machine
A **state machine** is a system that is always in one of a fixed set of states, and switches between them based on conditions.

Luna's healer has 3 states:
```
HEALTHY → MONITORING → HEALING → HEALTHY (cycle)
```
- **HEALTHY**: Score is good (≥70). Relax, nothing to do.
- **MONITORING**: Score has been poor for 1–4 consecutive readings. Starting to worry.
- **HEALING**: Score has been poor for ≥5 readings. Generate recovery plan, alert the user.

Transitions:
- `HEALTHY → MONITORING`: When a poor reading is received
- `MONITORING → HEALING`: When `poor_reading_count` reaches the threshold
- `HEALING → MONITORING`: Recovery plan attempted, checking if it worked
- `ANY → HEALTHY`: When score rises above 70 again

#### 2. Consecutive Count Pattern
A key technique: counting how many readings in a row meet a condition.

```python
if score < 70:
    self.poor_reading_count += 1   # increment each bad reading
else:
    self.poor_reading_count = 0    # RESET on any good reading
```

This is much smarter than a simple average — it catches sustained problems, not brief spikes.

#### 3. Incident Tracking
Each healing event is an "incident" — we log it so we can see patterns over time:
```json
{
  "started_at": "2026-05-19 21:30:00",
  "trigger": "heat stress",
  "score_at_start": 32,
  "actions_generated": ["shade plant", "mist leaves"],
  "resolved_at": null,
  "score_at_resolution": null
}
```

When Luna recovers, we fill in `resolved_at` and `score_at_resolution`. This history makes Phase 10 (the dashboard) very interesting.

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py`

Add at the bottom:
```
PSEUDOCODE — add to config.py:

# Self-healing settings
HEALING_THRESHOLD_SCORE = 60      # Score below this triggers monitoring
HEALING_TRIGGER_COUNT = 5         # How many consecutive poor readings before healing mode
HEALING_COOLDOWN_MINUTES = 15     # Don't generate a new healing plan within 15 min
INCIDENTS_FILE = "data/incidents.json"  # Where to log healing incidents
```

---

#### Step 2 — Build `python/healer.py`

```
PSEUDOCODE for healer.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: sys, os, json, time
Add UTF-8 fix
Import: datetime from datetime
Dual-import from config: HEALING_THRESHOLD_SCORE, HEALING_TRIGGER_COUNT,
    HEALING_COOLDOWN_MINUTES, INCIDENTS_FILE, AI_MODEL, GEMINI_API_KEY, MAX_RETRIES
Import: google.genai as genai

--- SYSTEM PROMPT ---
HEALER_PROMPT = """
You are Luna, a plant in distress. Based on your current health crisis,
generate 3 specific emergency recovery actions.

You MUST respond with ONLY valid JSON:
{
  "trigger": "one-word label: heat_stress OR drought OR poor_air OR general",
  "urgency": "critical" OR "high" OR "medium",
  "actions": [
    "action 1 — be very specific",
    "action 2 — be very specific",
    "action 3 — be very specific"
  ],
  "message": "Luna speaking in first person about what she needs right now"
}

Guidelines:
- Actions must be things a human can do RIGHT NOW
- Be specific: amounts, durations, techniques
- The message should be urgent but calm, first-person plant voice
"""

--- CLASS: SelfHealer ---

  __init__(self):
    self.client = genai.Client(api_key=GEMINI_API_KEY)
    self.state = "healthy"            ← start in healthy state
    self.poor_reading_count = 0       ← consecutive poor readings
    self.current_incident = None      ← dict of the active incident (or None)
    self.incidents = []               ← list of all past incidents
    self.last_healing_time = 0        ← timestamp of last healing plan (for cooldown)
    
    self._load_incidents()
    Print: "🔄 Self-Healing system ready"

  ---

  _load_incidents(self):
    Purpose: Load past incidents from disk
    
    If INCIDENTS_FILE doesn't exist: return
    
    Try:
      Open file, read content, if empty return
      Parse JSON
      self.incidents = parsed.get("incidents", [])
      Print: f"🔄 Loaded {len(self.incidents)} past incidents"
    
    Except: print warning

  ---

  _save_incidents(self):
    Purpose: Save incidents to disk
    
    Make sure folder exists (os.makedirs on the folder, exist_ok=True)
    
    data = {"incidents": self.incidents}
    
    Open INCIDENTS_FILE in write mode and json.dump with indent=2

  ---

  _detect_trigger(self, reading, score_result):
    Purpose: Identify WHAT is causing the poor health
    
    ← Look at the sensor readings to categorise the problem
    
    If reading["temperature"] > 32:
      return "heat_stress"
    
    If reading["humidity"] < 30:
      return "drought"
    
    If reading["air_quality"] > 900:
      return "poor_air"
    
    return "general"   ← catch-all

  ---

  _generate_healing_plan(self, reading, score_result, trigger):
    Purpose: Ask Gemini for emergency recovery actions
    
    Build a context string describing the crisis:
      crisis_context = (
          f"EMERGENCY: Luna's health score is {score_result['score']}/100\n"
          f"Current trigger: {trigger}\n"
          f"Temperature: {reading['temperature']}°C\n"
          f"Humidity: {reading['humidity']}%\n"
          f"Air quality: {reading['air_quality']} ppm\n"
          f"Consecutive poor readings: {self.poor_reading_count}\n"
          "Generate 3 specific emergency recovery actions."
      )
    
    full_prompt = HEALER_PROMPT + "\n\n" + crisis_context
    
    For attempt in range(MAX_RETRIES):
      Try:
        response = self.client.models.generate_content(
            model=AI_MODEL, contents=full_prompt
        )
        response_text = response.text.strip()
        
        Strip ```json wrapper if present (same pattern as other files)
        
        parsed = json.loads(response_text)
        
        Validate: must have "trigger", "actions", "message", "urgency"
        "actions" must be a list with at least 1 item
        
        return parsed
      
      Except json.JSONDecodeError: retry
      Except Exception as error: print warning, retry
    
    return None   ← all retries failed

  ---

  check(self, reading, score_result, voice=None):
    Purpose: Main method — call this on every reading cycle.
               Returns True if a healing action was triggered.
    
    If reading is None or score_result is None:
      return False
    
    score = score_result["score"]
    
    ── Case 1: Health is GOOD ────────────────────────────────────────────
    If score >= HEALING_THRESHOLD_SCORE:
      
      If self.state != "healthy":
        ← Luna was sick but now recovered!
        Print: f"✅ Luna has recovered! Score: {score}/100"
        
        If self.current_incident is not None:
          ← Close out the incident
          self.current_incident["resolved_at"] = now.strftime(...)
          self.current_incident["score_at_resolution"] = score
          self.incidents.append(self.current_incident)
          self._save_incidents()
          self.current_incident = None
        
        If voice: voice.speak("I feel much better now. Thank you for your care!")
      
      ← Reset state
      self.state = "healthy"
      self.poor_reading_count = 0
      return False
    
    ── Case 2: Health is POOR ────────────────────────────────────────────
    self.poor_reading_count += 1
    
    If self.poor_reading_count < HEALING_TRIGGER_COUNT:
      ← Still in monitoring — not bad enough yet
      self.state = "monitoring"
      Print: f"⚠️ Poor health detected ({self.poor_reading_count}/{HEALING_TRIGGER_COUNT})"
      return False
    
    ── Case 3: Sustained poor health — trigger healing ───────────────────
    self.state = "healing"
    
    Check cooldown:
      time_since_last = time.time() - self.last_healing_time
      If time_since_last < (HEALING_COOLDOWN_MINUTES * 60):
        minutes_left = round((HEALING_COOLDOWN_MINUTES * 60 - time_since_last) / 60)
        Print: f"⏳ Healing cooldown: {minutes_left} min remaining"
        return False
    
    ← Cooldown passed — generate a healing plan
    trigger = self._detect_trigger(reading, score_result)
    Print: f"🚨 Healing protocol triggered! Cause: {trigger}"
    
    plan = self._generate_healing_plan(reading, score_result, trigger)
    
    If plan is None:
      Print: "❌ Could not generate healing plan"
      return False
    
    ← Update cooldown timer
    self.last_healing_time = time.time()
    
    ← Create incident record
    self.current_incident = {
        "started_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "trigger": trigger,
        "score_at_start": score,
        "actions_generated": plan["actions"],
        "resolved_at": None,
        "score_at_resolution": None
    }
    
    ← Print the healing plan
    Print: "\n🌿 LUNA HEALING PROTOCOL 🌿"
    Print: f"Cause: {plan['trigger']} | Urgency: {plan['urgency'].upper()}"
    Print: f"Luna says: \"{plan['message']}\""
    Print: "Actions needed:"
    For i, action in enumerate(plan["actions"]):
      Print: f"  {i+1}. {action}"
    
    ← Speak if voice is available
    If voice:
      voice.speak(plan["message"])
    
    return True   ← healing was triggered

  ---

  get_status(self):
    Purpose: Return a short status string
    
    If self.state == "healthy":
      return f"✅ Healthy (0 poor readings)"
    Elif self.state == "monitoring":
      return f"⚠️ Monitoring ({self.poor_reading_count}/{HEALING_TRIGGER_COUNT} poor readings)"
    Else (healing):
      return f"🚨 Healing in progress (trigger: {current_incident's trigger if available})"

--- MAIN BLOCK (if __name__ == "__main__") ---

Create fake readings for 3 scenarios and test:

Scenario A — healthy reading (score will be high):
  Call check() → should print nothing special, return False

Scenario B — 6 consecutive stressed readings (temp=34, hum=22):
  Loop 6 times calling check() with the stressed reading
  → after 5th/6th call, healing protocol should trigger
  → healing plan should be printed

Scenario C — recovery reading (temp=22, humidity=60):
  Call check() → should print recovery message, return False

Print: "\n✅ Self-healing test complete!"
```

---

#### Step 3 — Update `main.py`

```
PSEUDOCODE — additions to main.py:

--- NEW IMPORTS ---
from python.healer import SelfHealer

--- IN main() FUNCTION ---
After creating scheduler, create:
  healer = SelfHealer()

In the reading loop, after health scoring and alerts:
  # Check if self-healing should be triggered
  healer.check(reading, score_result, voice)
  ← pass the voice object so Luna can speak her own healing requests
```

That's it — just those two lines. The healer handles everything internally.

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/healer.py` | New — full self-healing state machine |
| `python/config.py` | 4 new healing settings |
| `main.py` | `SelfHealer` created + `healer.check()` in the loop |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Not resetting `poor_reading_count` on good reading | Healer never resets, keeps triggering | Always `= 0` when score is good |
| Not implementing cooldown | Gemini called every reading during crisis | Check `last_healing_time` before generating |
| Putting the incident in `incidents` before it's resolved | Can't tell what was resolved vs active | Only append to `incidents` on resolution |
| Checking state before updating count | Count goes wrong on first bad reading | Always update count first, then check state |
| Forgetting to pass `voice=voice` to `check()` | Luna won't speak her healing request | Always pass voice from main.py |

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/healer.py` runs all 3 scenarios
- [ ] Scenario B triggers the healing protocol after exactly 5 consecutive poor readings
- [ ] Scenario C prints recovery message
- [ ] `data/incidents.json` is created after a healing event
- [ ] `uv run python main.py` — if you temporarily lower `HEALING_THRESHOLD_SCORE = 95` in config, healing triggers quickly
- [ ] The cooldown prevents repeated calls (check with a 1-minute cooldown temporarily)

---

### 🎊 Phase 9 Celebration (when you're done!)

🔄 **Luna can heal herself now!**

The self-healing system is the most sophisticated component you've built:
- State machine with 3 states
- Consecutive-reading pattern detection
- Cooldown to prevent API spam
- Incident tracking with open/close lifecycle
- Voice integration for urgent alerts

Combined with everything else, Luna now has:
- Sensors → health scoring → AI analysis → voice → memory → scheduling → **self-healing**

That's a complete autonomous care loop. You've built a real AI agent! 🌿

---

## ⏸️ STOP HERE

> 👉 Build `healer.py`, update `config.py` and `main.py`
>
> Test all 3 scenarios in the main block
>
> When you're done, type: **"Phase 9 done"** or **"Next"**
>
> I'll then give you **Phase 10: Dashboard** 📊

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
Phase 8  ✅ Daily Care Plans
Phase 9  🔨 You are here — Self-Healing
Phase 10 ⏳ Dashboard
```

**You are 90% done. One phase left.** 🌱

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 9 of 10*
