import json
import os
import sys
import time

from google import genai

# UTF-8 fix
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import (
    AI_MODEL,
    GEMINI_API_KEY,
    INCIDENTS_FILE,
    MAX_RETRIES,
)

HEALER_PROMPT = """
You are Luna, a plant in distress. Based on your current health crisis,
generate 3 specific emergency recovery actions.

You MUST respond with ONLY valid JSON:

{
  "trigger": "heat_stress OR drought OR poor_air OR general",
  "urgency": "critical OR high OR medium",
  "actions": [
    "action 1",
    "action 2",
    "action 3"
  ],
  "message": "First person message from Luna"
}
"""


class SelfHealer:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.state = "healthy"
        self.poor_reading_count = 0

        self.current_incident = None
        self.incidents = []

        self.last_healing_time = 0

        self._load_incidents()

        print("🔄 Self-Healing system ready")

    def _load_incidents(self):
        if not os.path.exists(INCIDENTS_FILE):
            return

        try:
            with open(INCIDENTS_FILE, encoding="utf-8") as file:
                content = file.read().strip()

                if not content:
                    return

                parsed = json.loads(content)

                self.incidents = parsed.get("incidents", [])

                print(f"🔄 Loaded {len(self.incidents)} past incidents")

        except Exception as error:
            print(f"⚠️ Incident load error: {error}")

    def _save_incidents(self):
        folder = os.path.dirname(INCIDENTS_FILE)

        if folder:
            os.makedirs(folder, exist_ok=True)

        data = {"incidents": self.incidents}

        with open(INCIDENTS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _detect_trigger(self, reading, score_result):
        if reading["temperature"] > 32:
            return "heat_stress"

        if reading["humidity"] < 30:
            return "drought"

        if reading["air_quality"] > 900:
            return "poor_air"

        return "general"

    def _generate_healing_plan(self, reading, score_result, trigger):
        crisis_context = (
            f"EMERGENCY: Luna's health score is "
            f"{score_result['score']}/100\n"
            f"Current trigger: {trigger}\n"
            f"Temperature: {reading['temperature']}°C\n"
            f"Humidity: {reading['humidity']}%\n"
            f"Air quality: {reading['air_quality']} ppm\n"
            f"Consecutive poor readings: "
            f"{self.poor_reading_count}\n"
            "Generate 3 specific emergency "
            "recovery actions."
        )

        full_prompt = HEALER_PROMPT + "\n\n" + crisis_context

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=AI_MODEL, contents=full_prompt
                )

                response_text = response.text.strip()

                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "")

                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                response_text = response_text.strip()

                parsed = json.loads(response_text)

                return parsed

            except json.JSONDecodeError:
                print(f"JSON parse failed (attempt {attempt + 1})")
                time.sleep(1)

            except Exception as error:
                print(f"Healing generation failed: {error}")
                time.sleep(1)

        return None
