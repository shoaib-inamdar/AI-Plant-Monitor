# 🌱 Luna — Phase 7: Health Scoring Engine
### Teaching Luna to Know How Sick She Is 🩺

> **Remember**: Read the pseudocode carefully, understand the logic, then write Python yourself. This phase involves real algorithmic thinking — the most satisfying kind!

---

## 🎉 Phase 6 Review — What Was Fixed

Your memory.py had **7 bugs** — all fixed. Here's the education in what went wrong:

| Bug | What You Wrote | What It Should Be |
|-----|---------------|-------------------|
| 1 — Wrong deque size | `deque(maxlen=MAX_AI_RESPONSES_IN_MEMORY)` for readings | `deque(maxlen=MAX_READINGSZ_IN_MEMORY)` |
| 2 — json.load() wrong arg | `json.load(MEMORY_FILE_PATH)` (a string path) | `json.load(f)` (the opened file object) |
| 3 — Wrong default type | `data.get("daily_summaries", [])` (list!) | `data.get("daily_summaries", {})` (dict) |
| 4 — All methods nested | `_save()`, `add_reading()`, etc. were indented inside `_load()` | Each method must be at class level (one indent) |
| 5 — Typo in method call | `self._update_daily_summmary(...)` (3 m's) | `self._update_daily_summary(...)` |
| 6 — Stats inside wrong block | Update lines were inside the `if date_str not in...` block | Must be outside — run every time, not just on first day |
| 7 — sum() on dicts | `sum(first_half / len(first_half))` | `sum(r[field] for r in first_half) / len(first_half)` |

> 💡 **The big lesson**: Python's indentation is not just style — it defines scope. A method indented inside another method becomes a nested function, not a class method. This is one of the most common beginner bugs in Python.

**Run this now to verify the fix works:**
```powershell
uv run python python/memory.py
```
You should see 15 readings added, temperature trend = "rising", humidity trend = "falling", and `data/luna_memory.json` created.

---

## ✅ Phase 7 — Health Scoring Engine

> **Stop after this phase and tell me "Phase 7 done" when finished!**

---

### 🎯 Goal

Build `python/health_scorer.py` — a **fast, rule-based health calculator** that scores Luna's health from 0–100 using sensor data directly, without calling the Gemini API.

By the end, you'll have:
- An instant health score on every single reading (not just every 30 seconds)
- Alert detection ("critical: temperature too high!")
- A weighted scoring system that reflects real plant biology
- Score history tracking so you can see Luna improving or declining
- A combined health report that merges sensor scores with memory trends

---

### 🤔 Why Both Rule-Based AND AI Scoring?

You might ask: "We already have Gemini giving health scores — why build another?"

Great question. Here's the difference:

| | Rule-Based (Phase 7) | AI-Based (Phase 4) |
|--|---------------------|-------------------|
| **Speed** | Instant (no network) | 1–3 seconds |
| **Cost** | Free, no API calls | Uses API quota |
| **Frequency** | Every reading (every 2s) | Every 30 seconds |
| **Consistency** | Always the same for same input | Can vary slightly |
| **Reasoning** | Simple thresholds | Complex, contextual |
| **Best for** | Real-time alerts, trend tracking | Care advice, explanations |

The professional approach is to use **both together**: rule-based for instant monitoring + AI for contextual advice. This is called a **hybrid system** — the same approach used in medical devices, autonomous cars, and industrial sensors.

The rule-based score also gives Gemini more context: instead of just sending raw numbers, you'll send "health score is 34 — stressed" and Gemini can give better advice.

---

### 🧠 Three Concepts to Understand First

#### 1. Weighted Scoring
Not all sensors are equally important for plant health. Temperature matters more than barometric pressure, for example.

**Weighted scoring** assigns a maximum contribution to each sensor:

| Sensor | Max Points | Why |
|--------|-----------|-----|
| Temperature | 30 | Most critical for plant survival |
| Humidity | 25 | Second most important |
| Air Quality | 20 | Affects photosynthesis |
| Rain/Moisture | 15 | Water availability |
| Pressure | 10 | Least impactful on most plants |
| **Total** | **100** | |

Each sensor gets a score between 0 and its max points based on how far from ideal it is.

#### 2. Scoring Functions
For each sensor, you need a function that maps the raw value to a score.

For **temperature**:
- 18–26°C = perfect = full 30 points
- Each degree outside ideal range = lose some points
- Below 5°C or above 40°C = 0 points (critical)

For **humidity**:
- 50–70% = perfect = full 25 points
- Each % outside ideal = lose points
- Below 20% or above 95% = 0 points

You can write this with simple `if/elif/else` chains.

#### 3. Alert Conditions
Beyond the score, some situations need immediate alerts regardless of the overall score. For example:
- Temperature > 38°C → "🚨 CRITICAL: Heat emergency!"
- Humidity < 15% → "🚨 CRITICAL: Drought conditions!"
- Air quality > 1500 ppm → "🚨 CRITICAL: Poor air quality!"

These are checked separately and returned as a list so `main.py` can print them and Luna's voice can speak them urgently.

---

### 🪜 Step-by-Step Instructions

---

#### Step 1 — Update `config.py`

Add these new settings at the bottom:

```
PSEUDOCODE — add to config.py:

# Ideal sensor ranges for health scoring
IDEAL_TEMP_MIN = 18.0      # °C — below this, start losing points
IDEAL_TEMP_MAX = 26.0      # °C — above this, start losing points
IDEAL_HUM_MIN = 50.0       # % — below this, start losing points
IDEAL_HUM_MAX = 70.0       # % — above this, start losing points
IDEAL_AQI_MAX = 600        # ppm — above this, start losing points (lower is better)

# Score weights (must add up to 100)
WEIGHT_TEMP = 30
WEIGHT_HUM = 25
WEIGHT_AQI = 20
WEIGHT_RAIN = 15
WEIGHT_PRES = 10

# Alert thresholds (these trigger urgent warnings)
ALERT_TEMP_HIGH = 35.0     # °C — above this is critical
ALERT_TEMP_LOW = 8.0       # °C — below this is critical
ALERT_HUM_LOW = 20.0       # % — below this is drought
ALERT_AQI_HIGH = 1200      # ppm — above this is poor air quality

# Score history
MAX_SCORE_HISTORY = 50     # Keep last 50 scores
```

---

#### Step 2 — Build `python/health_scorer.py`

```
PSEUDOCODE for health_scorer.py:
(Do NOT copy — write Python yourself!)

--- IMPORTS ---
Import: sys, os
Add UTF-8 fix (same as other files)
Import: datetime from datetime
Import: deque from collections

Dual-import for config:
    Try: from python.config import (all the new constants you added above)
    Except ImportError: from config import ...

--- CLASS: HealthScorer ---

  __init__(self):
    self.score_history = deque(maxlen=MAX_SCORE_HISTORY)
    Print: "🩺 Health Scorer ready"

  ---

  _score_temperature(self, temp):
    Purpose: Score temperature from 0 to WEIGHT_TEMP (30 points)
    
    If IDEAL_TEMP_MIN <= temp <= IDEAL_TEMP_MAX:
      return WEIGHT_TEMP    ← perfect, full points
    
    If temp < IDEAL_TEMP_MIN:
      How far below ideal?
        distance = IDEAL_TEMP_MIN - temp
      Lose 2 points per degree below ideal
        score = WEIGHT_TEMP - (distance * 2)
      Clamp to 0 (never go negative):
        return max(0, score)
    
    If temp > IDEAL_TEMP_MAX:
      How far above ideal?
        distance = temp - IDEAL_TEMP_MAX
      Lose 2 points per degree above ideal
        score = WEIGHT_TEMP - (distance * 2)
      Clamp to 0:
        return max(0, score)

  ---

  _score_humidity(self, hum):
    Purpose: Score humidity from 0 to WEIGHT_HUM (25 points)
    
    Same pattern as temperature:
    If IDEAL_HUM_MIN <= hum <= IDEAL_HUM_MAX:
      return WEIGHT_HUM
    
    If hum < IDEAL_HUM_MIN:
      distance = IDEAL_HUM_MIN - hum
      Lose 0.5 points per % below ideal  ← humidity is less sensitive than temp
      return max(0, WEIGHT_HUM - (distance * 0.5))
    
    If hum > IDEAL_HUM_MAX:
      distance = hum - IDEAL_HUM_MAX
      Lose 0.3 points per % above ideal  ← too high is less bad than too low
      return max(0, WEIGHT_HUM - (distance * 0.3))

  ---

  _score_air_quality(self, aqi):
    Purpose: Score air quality from 0 to WEIGHT_AQI (20 points)
    
    Note: for AQI, LOWER is better (unlike temp/humidity where middle is best)
    
    If aqi <= IDEAL_AQI_MAX (600):
      return WEIGHT_AQI    ← great air quality
    
    If aqi > IDEAL_AQI_MAX:
      How far above ideal?
        distance = aqi - IDEAL_AQI_MAX
      Lose 1 point per 50 ppm above ideal:
        score = WEIGHT_AQI - (distance / 50)
      return max(0, score)

  ---

  _score_rain(self, rain):
    Purpose: Score rain sensor from 0 to WEIGHT_RAIN (15 points)
    
    This is a binary sensor (0 or 1), not a continuous value.
    Think of it as: is there moisture available?
    
    If rain == 1:
      return WEIGHT_RAIN    ← rain is detected, great for the plant
    Else:
      ← No rain. This doesn't mean the plant is dying —
        soil might still be moist from earlier watering.
        Give partial credit: 8 points (just over half)
      return 8

  ---

  _score_pressure(self, pressure):
    Purpose: Score pressure from 0 to WEIGHT_PRES (10 points)
    
    Ideal range: 1000–1020 hPa
    
    If 1000 <= pressure <= 1020:
      return WEIGHT_PRES    ← ideal
    
    Calculate distance from nearest ideal boundary:
      If pressure < 1000:
        distance = 1000 - pressure
      Else (pressure > 1020):
        distance = pressure - 1020
    
    Lose 0.5 points per hPa outside ideal:
      score = WEIGHT_PRES - (distance * 0.5)
    return max(0, score)

  ---

  _check_alerts(self, reading):
    Purpose: Detect urgent alert conditions regardless of score
    
    Create an empty list: alerts = []
    
    Check each alert condition:
    
    If reading["temperature"] > ALERT_TEMP_HIGH:
      alerts.append(f"🚨 CRITICAL: Temperature {reading['temperature']}°C — heat emergency!")
    
    If reading["temperature"] < ALERT_TEMP_LOW:
      alerts.append(f"🚨 CRITICAL: Temperature {reading['temperature']}°C — dangerously cold!")
    
    If reading["humidity"] < ALERT_HUM_LOW:
      alerts.append(f"🚨 CRITICAL: Humidity {reading['humidity']}% — drought conditions!")
    
    If reading["air_quality"] > ALERT_AQI_HIGH:
      alerts.append(f"🚨 WARNING: Air quality {reading['air_quality']} ppm — poor ventilation!")
    
    return alerts

  ---

  calculate_score(self, reading):
    Purpose: Main method — calculate full health score for one reading
    
    If reading is None:
      return None
    
    Step 1: Calculate sub-scores for each sensor:
      temp_score = self._score_temperature(reading["temperature"])
      hum_score = self._score_humidity(reading["humidity"])
      aqi_score = self._score_air_quality(reading["air_quality"])
      rain_score = self._score_rain(reading["rain"])
      pres_score = self._score_pressure(reading["pressure"])
    
    Step 2: Add them up and round:
      total = temp_score + hum_score + aqi_score + rain_score + pres_score
      total = round(total)
      total = max(0, min(100, total))    ← clamp between 0 and 100
    
    Step 3: Determine status label:
      If total >= 85:   status = "excellent"
      Elif total >= 70: status = "good"
      Elif total >= 50: status = "mild_stress"
      Elif total >= 30: status = "stressed"
      Else:             status = "critical"
    
    Step 4: Check alerts:
      alerts = self._check_alerts(reading)
    
    Step 5: Build result dictionary:
      result = {
          "timestamp": reading["timestamp"],
          "score": total,
          "status": status,
          "alerts": alerts,
          "breakdown": {
              "temperature": round(temp_score, 1),
              "humidity": round(hum_score, 1),
              "air_quality": round(aqi_score, 1),
              "rain": round(rain_score, 1),
              "pressure": round(pres_score, 1)
          }
      }
    
    Step 6: Store in history:
      self.score_history.append(result)
    
    Step 7: Return result

  ---

  get_score_trend(self):
    Purpose: Is Luna's health improving or getting worse?
    
    recent = list(self.score_history)
    
    If len(recent) < 4:
      return "insufficient data"
    
    mid = len(recent) // 2
    avg_first = sum(r["score"] for r in recent[:mid]) / (len(recent) // 2)
    avg_second = sum(r["score"] for r in recent[mid:]) / (len(recent) - len(recent) // 2)
    
    difference = avg_second - avg_first
    
    If difference > 3:    ← more than 3 points higher = improving
      return "improving 📈"
    Elif difference < -3: ← more than 3 points lower = declining
      return "declining 📉"
    Else:
      return "stable ➡️"

  ---

  format_score(self, result):
    Purpose: Pretty-print the score result for the terminal
    
    If result is None:
      return "No score calculated"
    
    Choose an emoji based on score:
      If score >= 85: indicator = "🟢"
      Elif score >= 50: indicator = "🟡"
      Else: indicator = "🔴"
    
    Build a formatted string:
      f"{indicator} Health Score: {result['score']}/100 — {result['status'].upper()}"
      f"  Breakdown: Temp={breakdown['temperature']} | Hum={breakdown['humidity']} | 
                    AQI={breakdown['air_quality']} | Rain={breakdown['rain']} | 
                    Pres={breakdown['pressure']}"
    
    If there are alerts, add each one on a new line.
    
    Return the complete string.

--- MAIN BLOCK (if __name__ == "__main__") ---
Purpose: Test with fake readings across a range of conditions

Create a HealthScorer.

Test 3 scenarios:

Scenario 1 — Perfect conditions:
  reading = {temperature: 22, humidity: 60, air_quality: 400, rain: 1, 
             pressure: 1013, timestamp: now, status: "ok"}
  Print: "Test 1 — Perfect conditions:"
  result = scorer.calculate_score(reading)
  Print: scorer.format_score(result)

Scenario 2 — Stressed plant:
  reading = {temperature: 33, humidity: 25, air_quality: 700, rain: 0, 
             pressure: 1013, timestamp: now, status: "ok"}
  Print: "\nTest 2 — Stressed plant:"
  result = scorer.calculate_score(reading)
  Print: scorer.format_score(result)

Scenario 3 — Critical emergency:
  reading = {temperature: 40, humidity: 12, air_quality: 1500, rain: 0, 
             pressure: 1013, timestamp: now, status: "ok"}
  Print: "\nTest 3 — Emergency:"
  result = scorer.calculate_score(reading)
  Print: scorer.format_score(result)
  
Print: f"\nHealth trend: {scorer.get_score_trend()}"
Print: "\n✅ Health scorer test complete!"
```

---

#### Step 3 — Update `main.py`

Add health scoring to every reading cycle:

```
PSEUDOCODE — additions to main.py:

--- NEW IMPORTS ---
from python.health_scorer import HealthScorer

--- IN main() FUNCTION ---
After creating memory, create:
  scorer = HealthScorer()

In the reading loop, after memory.add_reading(reading):
  score_result = scorer.calculate_score(reading)
  
  If score_result is not None:
    Print scorer.format_score(score_result)
    
    # Print any urgent alerts immediately
    For each alert in score_result["alerts"]:
      Print: alert
      voice.speak(alert)   ← Luna speaks emergency alerts!

In the AI section, pass the score to the brain so Gemini knows it:
  ← Update the reading dict before sending to AI:
    reading_with_score = reading.copy()
    reading_with_score["rule_based_score"] = score_result["score"] if score_result else "unknown"
    reading_with_score["rule_based_status"] = score_result["status"] if score_result else "unknown"
    
    response = brain.analyse(reading_with_score)   ← use enriched reading
```

#### Step 4 — Update `ai_brain.py` to Use the Score

In `_build_prompt()`, add the rule-based score to the prompt text so Gemini sees it:

```
PSEUDOCODE — add to _build_prompt() in ai_brain.py:

After the existing sensor lines, add:

If "rule_based_score" is in reading:
    Add this line to the prompt:
    f"Rule-based health score: {reading['rule_based_score']}/100 ({reading['rule_based_status']})"
    "Please consider this score in your assessment."
```

---

### 📁 Files Changed in This Phase

| File | What Changed |
|------|-------------|
| `python/health_scorer.py` | New — the full health scoring engine |
| `python/config.py` | Added ideal ranges, weights, alert thresholds |
| `main.py` | Score calculated every reading, alerts spoken |
| `python/ai_brain.py` | `_build_prompt()` now includes rule-based score |

---

### ⚠️ Common Mistakes to Avoid

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Weights that don't add to 100 | Score can exceed 100 or never reach it | Always verify: 30+25+20+15+10 = 100 ✅ |
| Not clamping score to 0–100 | Can get -5 or 105 for extreme values | Always do `max(0, min(100, total))` |
| Checking alerts inside scoring functions | Mixes two responsibilities | Keep `_check_alerts()` separate |
| Making rain score 0 when rain==0 | Plant doesn't instantly die without rain | Give partial credit (8/15) when dry |
| Printing alerts inside `calculate_score()` | Hard to test, mixes output with logic | Return alerts in the dict, print in `main.py` |

---

### ✅ How to Know You Did It Right

- [ ] `uv run python python/health_scorer.py` runs and shows 3 test results
- [ ] Test 1 (perfect conditions) scores 85–100
- [ ] Test 2 (stressed) scores 35–60
- [ ] Test 3 (emergency) scores below 30 AND shows alert messages
- [ ] `uv run python main.py` shows a health score line on every single reading
- [ ] When you temporarily set `ALERT_TEMP_HIGH = 19` in config, every reading triggers an alert

---

### 🎊 Phase 7 Celebration (when you're done!)

🩺 **Luna now has a medical monitoring system!**

You've built something real engineers call an **expert system** — a rule-based decision engine that encodes domain knowledge (plant biology) into code. Combined with the AI brain from Phase 4, Luna now has:

- Fast rule-based health monitoring (every 2 seconds)
- Contextual AI reasoning (every 30 seconds)
- Alert detection for emergencies
- Score history and trend analysis
- Hybrid system that's better than either alone

That's a genuinely impressive architecture! 🌿

---

## ⏸️ STOP HERE

> 👉 Build `health_scorer.py`, update `config.py`, `main.py`, and `ai_brain.py`
>
> Test all 3 scenarios in the main block
>
> When you're done, type: **"Phase 7 done"** or **"Next"**
>
> I'll then give you **Phase 8: Daily Care Plans** 📅

---

## 📊 Project Progress

```
Phase 1  ✅ Setup complete
Phase 2  ✅ Sensor simulator running
Phase 3  ✅ Serial bridge — data pipeline
Phase 4  ✅ AI Brain — Luna thinks
Phase 5  ✅ Luna's Voice — speaks & listens
Phase 6  ✅ Memory & Data — Luna remembers
Phase 7  🔨 You are here — Health Scoring
Phase 8  ⏳ Daily Care Plans
Phase 9  ⏳ Self-Healing
Phase 10 ⏳ Dashboard
```

You're **70% done** 🌿 Three phases left — you are almost there!

---

*Guide Version: 1.0 | Project: Luna AI Plant Care System | Phase 7 of 10*
