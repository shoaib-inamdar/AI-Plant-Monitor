import sys

# Fix emoji display on Windows PowerShell when running this file directly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import time

from google import genai

try:
    from python.config import (
        AI_MODEL,
        GEMINI_API_KEY,
        GROQ_API_KEY,
        MAX_RETRIES,
        USE_BACKUP_AI,
    )
except ImportError:
    # pyrefly: ignore [missing-import]
    from config import (
        AI_MODEL,
        GEMINI_API_KEY,
        MAX_RETRIES,
    )


LUNA_SYSTEM_PROMPT = """
You are Luna, a wise and gentle plant who monitors her own environment.

You speak in first person as the plant — warm, calm, slightly poetic, but also practical.

You receive sensor readings about your environment and analyze your own health.

You MUST always respond with valid JSON and nothing else.
Do not include any explanation outside the JSON.

Your JSON response must have exactly these fields:
{
  "health_score": number (0 to 100),
  "status": "excellent" | "good" | "mild_stress" | "stressed" | "critical",
  "message": "1-2 sentence message in first person as Luna",
  "actions": ["action1", "action2"],
  "reason": "short technical explanation"
}

Guidelines:
- Speak like a living plant (gentle, aware, slightly emotional)
- Be concise but meaningful
- Do NOT add extra keys
- Do NOT break JSON format

Sensor ranges reference:
- Temperature: 18-26°C ideal
- Humidity: 50-70%, is ideal
- Air quality: below 600 ppm is good
- Rain: 0 = no rain, 1 = rain detected
- Pressure: 1000-1020 hPa normal
"""


class LunaBrain:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = AI_MODEL
        self.last_response = None

        print("🧠 Luna's AI brain initialised")

    def _build_prompt(self, reading):
        """Format the sensor reading as a clear message to send to Gemini."""

        prompt = (
            "Current sensor readings for Luna:\n"
            f"Timestamp: {reading['timestamp']}\n"
            f"Temperature: {reading['temperature']}°C\n"
            f"Humidity: {reading['humidity']}%\n"
            f"Air Quality: {reading['air_quality']} ppm\n"
            f"Rain detected: {'Yes' if reading['rain'] == 1 else 'No'}\n"
            f"Barometric Pressure: {reading['pressure']} hPa\n"
            f"Sensor status: {reading['status']}\n"
        )

        # Include rule-based score if main.py enriched the reading with it
        if "rule_based_score" in reading:
            prompt += (
                f"Rule-based health score: {reading['rule_based_score']}/100 "
                f"({reading['rule_based_status']})\n"
                "Please consider this score in your assessment.\n"
            )

        prompt += (
            "\nPlease analyse these readings and respond with your JSON assessment."
        )
        return prompt

    def analyse(self, reading):
        """Purpose: Send a reading to Gemini and get Luna's response back"""

        if reading is None:
            return None

        prompt = self._build_prompt(reading)
        full_prompt = LUNA_SYSTEM_PROMPT + "\n\n" + prompt

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name, contents=full_prompt
                )

                response_text = response.text.strip()

                if response_text.startswith("```"):
                    lines = response_text.splitlines()
                    lines = lines[1:-1]
                    response_text = "\n".join(lines).strip()

                parsed = json.loads(response_text)
                required = ["health_score", "status", "message", "actions", "reason"]

                for field in required:
                    if field not in parsed:
                        raise ValueError(f"Missing field:{field}")

                self.last_response = parsed
                return parsed

            except json.JSONDecodeError:
                print(
                    f"⚠️ Attempt {attempt + 1}: Gemini returned invalid JSON. Retrying..."
                )
                time.sleep(1)

            except Exception as error:
                print(f"⚠️ Attempt {attempt + 1}: API error — {error}")
                time.sleep(2)

        print("❌ All retries failed. Using fallback response.")
        return {
            "health_score": 50,
            "status": "unknown",
            "message": "I'm having trouble thinking right now. Please check my connections.",
            "actions": ["check system", "retry later"],
            "reason": "AI brain temporarily unavailable",
        }

    def explain_decision(self):
        """Purpose: Explainable AI — Why did you say that?"""

        if self.last_response is None:
            return "I haven't analysed any readings yet."

        response = self.last_response

        actions_text = ""
        for action in response["actions"]:
            actions_text += f"  → {action}\n"

        return (
            "🌿 Luna's Last Assessment:\n"
            f"Health Score: {response['health_score']}/100\n"
            f"Status: {response['status'].upper()}\n\n"
            f"What Luna said: {response['message']}\n\n"
            f"Why: {response['reason']}\n\n"
            "Recommended actions:\n"
            f"{actions_text}"
        )

    def format_response(self, response):
        """Purpose: Pretty-print a response for the terminal"""
        if response is None:
            return "No response"

        score = response["health_score"]

        if score > 70:
            indicator = "🟢"
        elif score >= 40:
            indicator = "🟡"
        else:
            indicator = "🔴"

        actions_text = ""
        for action in response["actions"]:
            actions_text += f"  • {action}\n"

        return (
            f"{indicator} Health Score: {score}/100\n"
            f"Status: {response['status'].upper()}\n\n"
            f'🌱 Luna says: "{response["message"]}"\n\n'
            "🔧 Actions:\n"
            f"{actions_text}"
        )


if __name__ == "__main__":
    fake_reading = {
        "timestamp": "2026-05-01 10:00:00",
        "temperature": 32.0,
        "humidity": 22.0,
        "air_quality": 650,
        "rain": 0,
        "pressure": 1010.50,
        "status": "ok",
    }

    brain = LunaBrain()
    print("Sending reading to Luna's AI brain...")
    response = brain.analyse(fake_reading)
    print(brain.format_response(response))
    print("\n\n")
    print(brain.explain_decision())
