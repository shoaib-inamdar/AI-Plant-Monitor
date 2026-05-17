import sys

# UTF-8 fix (must be first)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os, json
from datetime import datetime
from collections import deque

try:
    from python.config import (
        MEMORY_FILE_PATH, MAX_READINGSZ_IN_MEMORY,
        MAX_AI_RESPONSES_IN_MEMORY, TREND_WINDOW
    )
except ImportError:
    from config import (
        MEMORY_FILE_PATH, MAX_READINGSZ_IN_MEMORY,
        MAX_AI_RESPONSES_IN_MEMORY, TREND_WINDOW
    )


class LunaMemory:
    def __init__(self):
        self.readings = deque(maxlen=MAX_READINGSZ_IN_MEMORY)
        self.ai_responses = deque(maxlen=MAX_AI_RESPONSES_IN_MEMORY)
        self.daily_summaries = {}

        self._load()
        print("💾 Memory system ready")


    def _load(self):
        """Load saved data from luna_memory.json on startup."""

        if not os.path.isfile(MEMORY_FILE_PATH):
            return

        try:
            with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:          # empty file — treat as fresh start
                    return
                data = json.loads(content)

            for item in data.get("readings", []):
                self.readings.append(item)

            for item in data.get("ai_responses", []):
                self.ai_responses.append(item)


            self.daily_summaries = data.get("daily_summaries", {})

            print(f"💾 Loaded {len(self.readings)} readings from memory")

        except Exception as error:
            print(f"⚠️ Could not load memory: {error}")

    def _save(self):
        """Save current memory to luna_memory.json."""

        folder = os.path.dirname(MEMORY_FILE_PATH)
        if folder:
            os.makedirs(folder, exist_ok=True)

        data = {
            "readings": list(self.readings),
            "ai_responses": list(self.ai_responses),
            "daily_summaries": self.daily_summaries,
            "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


    def add_reading(self, reading):
        """Store a new sensor reading in memory."""

        if reading is None:
            return

        self.readings.append(reading)

        today = datetime.now().strftime("%Y-%m-%d")
        # BUG FIX 5: typo — was calling _update_daily_summmary (3 m's)
        self._update_daily_summary(today, reading)
        self._save()


    def add_ai_response(self, response):
        """Store a new AI response in memory."""

        if response is None:
            return

        response_with_time = response.copy()
        response_with_time["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ai_responses.append(response_with_time)
        self._save()


    def _update_daily_summary(self, date_str, reading):
        """Update running totals for a given day."""

        if date_str not in self.daily_summaries:
            self.daily_summaries[date_str] = {
                "count": 0,
                "temp_sum": 0.0,
                "hum_sum": 0.0,
                "aqi_sum": 0,
                "rain_count": 0,
                "date": date_str
            }

        day = self.daily_summaries[date_str]

        day["count"] += 1
        day["temp_sum"] += reading["temperature"]
        day["hum_sum"] += reading["humidity"]
        day["aqi_sum"] += reading["air_quality"]
        day["rain_count"] += reading["rain"]


    def get_daily_summary(self, date_str=None):
        """Get calculated averages for a given day."""

        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        if date_str not in self.daily_summaries:
            return None

        day = self.daily_summaries[date_str]
        count = day["count"]

        if count == 0:
            return None

        return {
            "date": date_str,
            "reading_count": count,
            "avg_temperature": round(day["temp_sum"] / count, 1),
            "avg_humidity": round(day["hum_sum"] / count, 1),
            "avg_air_quality": round(day["aqi_sum"] / count),
            "rain_events": day["rain_count"]
        }


    def get_recent_readings(self, n=10):
        """Return the last n readings as a list."""
        return list(self.readings)[-n:]


    def get_trend(self, field="temperature"):
        """Detect if a field is rising, falling, or stable."""

        recent = self.get_recent_readings(TREND_WINDOW)

        if len(recent) < 4:
            return "insufficient data"

        mid = len(recent) // 2
        first_half = recent[:mid]
        second_half = recent[mid:]

        avg_first = sum(r[field] for r in first_half) / len(first_half)
        avg_second = sum(r[field] for r in second_half) / len(second_half)

        difference = avg_second - avg_first

        if difference > 1.0:
            return "rising"
        elif difference < -1.0:
            return "falling"
        else:
            return "stable"


    def get_summary_text(self):
        """Generate a human-readable summary of current memory state."""

        recent = self.get_recent_readings(5)

        if not recent:
            return "No readings in memory yet."

        last = recent[-1]
        temp_trend = self.get_trend("temperature")
        hum_trend = self.get_trend("humidity")
        today_summary = self.get_daily_summary()

        lines = [
            "📊 Luna Memory Summary:",
            f"  Latest:            {last['temperature']}°C, {last['humidity']}% RH",
            f"  Temperature trend: {temp_trend}",
            f"  Humidity trend:    {hum_trend}",
            f"  Readings stored:   {len(self.readings)}",
        ]

        if today_summary:
            lines += [
                f"  Today ({today_summary['date']}):",
                f"    Avg temp:     {today_summary['avg_temperature']}°C",
                f"    Avg humidity: {today_summary['avg_humidity']}%",
                f"    Rain events:  {today_summary['rain_events']}",
            ]

        return "\n".join(lines)



if __name__ == "__main__":
    memory = LunaMemory()
    print("Testing memory system...\n")

    for i in range(15):
        fake_reading = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(22.0 + (i * 0.3), 1),
            "humidity": round(65.0 - (i * 0.5), 1),
            "air_quality": 420 + (i * 5),
            "rain": 0,
            "pressure": 1013.0,
            "status": "ok"
        }
        memory.add_reading(fake_reading)
        print(f"Added reading {i + 1}: Temp={fake_reading['temperature']}°C")

    print()
    print(memory.get_summary_text())

    print("\nTrends:")
    print(f"  Temperature: {memory.get_trend('temperature')}")
    print(f"  Humidity:    {memory.get_trend('humidity')}")

    print("\nToday's summary:")
    print(memory.get_daily_summary())

    print("\n✅ Memory test complete! Check data/luna_memory.json")