import sys
import os
import json
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from datetime import datetime

try:
    from python.config import (
        HEALING_THRESHOLD_SCORE, HEALING_TRIGGER_COUNT,
        HEALING_COOLDOWN_MINUTES, INCIDENTS_FILE,
        AI_MODEL, GEMINI_API_KEY, MAX_RETRIES
    )
except ImportError:
    from config import (
        HEALING_THRESHOLD_SCORE, HEALING_TRIGGER_COUNT,
        HEALING_COOLDOWN_MINUTES, INCIDENTS_FILE,
        AI_MODEL, GEMINI_API_KEY, MAX_RETRIES
    )

import google.genai as genai


HEALER_PROMPT = """
You are Luna, a plant in distress. Based on your current health crisis,
generate 3 specific emergency recovery actions a human can take right now.

Respond with ONLY valid JSON — no markdown, no explanation outside the JSON:
{
  "trigger": "heat_stress OR drought OR poor_air OR general",
  "urgency": "critical OR high OR medium",
  "actions": [
    "action 1 — be very specific with amounts and durations",
    "action 2 — be very specific",
    "action 3 — be very specific"
  ],
  "message": "Luna speaking urgently in first person about what she needs right now"
}

Rules:
- "trigger" must be exactly one of: heat_stress, drought, poor_air, general
- "urgency" must be exactly one of: critical, high, medium
- "actions" must be a list of exactly 3 strings
- "message" must be 1-2 sentences in first-person plant voice, urgent but calm
- Actions must be things a human can do immediately
"""



class SelfHealer:


    STATE_HEALTHY    = "healthy"
    STATE_MONITORING = "monitoring"
    STATE_HEALING    = "healing"

    def __init__(self):
        self.client             = genai.Client(api_key=GEMINI_API_KEY)
        self.state              = self.STATE_HEALTHY
        self.poor_reading_count = 0
        self.current_incident   = None   # dict of the active incident
        self.incidents          = []     # list of all resolved incidents
        self.last_healing_time  = 0      # unix timestamp of last plan generated

        self._load_incidents()
        print("🔄 Self-Healing system ready")



    def _load_incidents(self):
        """Load past incidents from disk."""
        if not os.path.isfile(INCIDENTS_FILE):
            return
        try:
            with open(INCIDENTS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return
                data = json.loads(content)
            self.incidents = data.get("incidents", [])
            if self.incidents:
                print(f"🔄 Loaded {len(self.incidents)} past incident(s)")
        except Exception as error:
            print(f"⚠️ Could not load incidents: {error}")

    def _save_incidents(self):
        """Save incidents list to disk."""
        folder = os.path.dirname(INCIDENTS_FILE)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(INCIDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump({"incidents": self.incidents}, f, indent=2)



    def _detect_trigger(self, reading):
        """Identify the most likely cause of the poor health."""
        if reading["temperature"] > 32:
            return "heat_stress"
        if reading["humidity"] < 30:
            return "drought"
        if reading["air_quality"] > 900:
            return "poor_air"
        return "general"



    def _generate_healing_plan(self, reading, score_result, trigger):
        """Ask Gemini for 3 specific emergency recovery actions."""

        crisis_context = (
            f"EMERGENCY: Luna's health score is {score_result['score']}/100\n"
            f"Trigger: {trigger}\n"
            f"Temperature: {reading['temperature']}°C\n"
            f"Humidity: {reading['humidity']}%\n"
            f"Air quality: {reading['air_quality']} ppm\n"
            f"Rain detected: {'Yes' if reading['rain'] == 1 else 'No'}\n"
            f"Consecutive poor readings: {self.poor_reading_count}\n"
            "Generate 3 specific emergency recovery actions."
        )

        full_prompt = HEALER_PROMPT + "\n\n" + crisis_context

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=AI_MODEL,
                    contents=full_prompt
                )

                response_text = response.text.strip()


                if response_text.startswith("```"):
                    lines = response_text.splitlines()
                    if len(lines) >= 2:
                        lines = lines[1:-1]
                    response_text = "\n".join(lines).strip()

                parsed = json.loads(response_text)


                required = ["trigger", "urgency", "actions", "message"]
                for field in required:
                    if field not in parsed:
                        raise ValueError(f"Missing field: {field}")

                if not isinstance(parsed["actions"], list) or len(parsed["actions"]) == 0:
                    raise ValueError("'actions' must be a non-empty list")

                return parsed

            except json.JSONDecodeError:
                print(f"⚠️ Healing attempt {attempt + 1}: Invalid JSON. Retrying...")
                time.sleep(1)

            except Exception as error:
                print(f"⚠️ Healing attempt {attempt + 1}: {error}")
                time.sleep(2)

        return None  # all retries failed



    def check(self, reading, score_result, voice=None):
        """
        Call this on every reading cycle.
        Returns True if a healing protocol was triggered this cycle.
        """
        if reading is None or score_result is None:
            return False

        score = score_result["score"]
        now   = datetime.now()


        if score >= HEALING_THRESHOLD_SCORE:

            if self.state != self.STATE_HEALTHY:

                print(f"\n✅ Luna has recovered! Score back to {score}/100")

                if self.current_incident is not None:
                    self.current_incident["resolved_at"]        = now.strftime("%Y-%m-%d %H:%M:%S")
                    self.current_incident["score_at_resolution"] = score
                    self.incidents.append(self.current_incident)
                    self._save_incidents()
                    self.current_incident = None
                    print(f"📋 Incident saved. Total incidents logged: {len(self.incidents)}")

                if voice:
                    voice.speak("I feel much better now. Thank you for your care!")


            self.state              = self.STATE_HEALTHY
            self.poor_reading_count = 0
            return False


        self.poor_reading_count += 1

        if self.poor_reading_count < HEALING_TRIGGER_COUNT:

            self.state = self.STATE_MONITORING
            print(
                f"⚠️  Monitoring poor health "
                f"({self.poor_reading_count}/{HEALING_TRIGGER_COUNT} readings)"
            )
            return False


        self.state = self.STATE_HEALING


        time_since_last = time.time() - self.last_healing_time
        cooldown_seconds = HEALING_COOLDOWN_MINUTES * 60

        if time_since_last < cooldown_seconds:
            minutes_left = round((cooldown_seconds - time_since_last) / 60, 1)
            print(f"⏳ Healing cooldown: {minutes_left} min remaining")
            return False


        trigger = self._detect_trigger(reading)
        print(f"\n🚨 Healing protocol triggered! Cause: {trigger.upper()}")

        plan = self._generate_healing_plan(reading, score_result, trigger)

        if plan is None:
            print("❌ Could not generate healing plan — will retry next cycle")
            return False


        self.last_healing_time = time.time()


        self.current_incident = {
            "started_at":         now.strftime("%Y-%m-%d %H:%M:%S"),
            "trigger":            trigger,
            "score_at_start":     score,
            "actions_generated":  plan["actions"],
            "resolved_at":        None,
            "score_at_resolution": None,
        }


        urgency_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡"}
        icon = urgency_icons.get(plan.get("urgency", "medium"), "🟡")

        print(f"\n{'='*50}")
        print(f"🌿 LUNA HEALING PROTOCOL  {icon} {plan.get('urgency','').upper()}")
        print(f"{'='*50}")
        print(f"Trigger : {plan['trigger']}")
        print(f"Luna says: \"{plan['message']}\"")
        print("Actions needed NOW:")
        for i, action in enumerate(plan["actions"], start=1):
            print(f"  {i}. {action}")
        print(f"{'='*50}\n")


        if voice:
            voice.speak(plan["message"])

        return True  # healing was triggered



    def get_status(self):
        """Return a short human-readable status string."""
        if self.state == self.STATE_HEALTHY:
            return "✅ Healthy"
        if self.state == self.STATE_MONITORING:
            return (
                f"⚠️ Monitoring "
                f"({self.poor_reading_count}/{HEALING_TRIGGER_COUNT} poor readings)"
            )

        trigger = (
            self.current_incident["trigger"]
            if self.current_incident else "unknown"
        )
        return f"🚨 Healing in progress (trigger: {trigger})"



if __name__ == "__main__":
    print("🧪 Testing Self-Healing Module\n")

    healer = SelfHealer()

    def _fake(temp, hum, aqi, rain=0, pressure=1013.0):
        return {
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temp,
            "humidity":    hum,
            "air_quality": aqi,
            "rain":        rain,
            "pressure":    pressure,
            "status":      "ok",
        }


    try:
        from python.health_scorer import HealthScorer
    except ImportError:
        from health_scorer import HealthScorer

    scorer = HealthScorer()


    print("━" * 50)
    print("Scenario A — Healthy reading (should do nothing)")
    reading = _fake(temp=22, hum=62, aqi=420)
    result  = scorer.calculate_score(reading)
    triggered = healer.check(reading, result)
    print(f"Healing triggered: {triggered}  |  Status: {healer.get_status()}")


    print("\n" + "━" * 50)
    print("Scenario B — 6 consecutive stressed readings (healing should trigger on #5)")

    stressed = _fake(temp=37, hum=18, aqi=500)
    for i in range(1, 7):
        s_result = scorer.calculate_score(stressed)
        print(f"\n  Reading {i}: Score={s_result['score']}")
        triggered = healer.check(stressed, s_result, voice=None)
        print(f"  Healing triggered: {triggered}  |  Status: {healer.get_status()}")
        if triggered:
            break  # stop after first trigger — healing plan already printed


    print("\n" + "━" * 50)
    print("Scenario C — Recovery reading (should print recovery message)")
    healthy = _fake(temp=22, hum=62, aqi=420)
    h_result = scorer.calculate_score(healthy)
    healer.check(healthy, h_result)
    print(f"Final status: {healer.get_status()}")

    print("\n✅ Self-healing test complete!")
    print("Check data/incidents.json if a healing event was triggered.")
