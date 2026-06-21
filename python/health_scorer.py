import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from collections import deque
from datetime import datetime

try:
    from python.config import (
        ALERT_AQI_HIGH,
        ALERT_HUM_LOW,
        ALERT_SOIL_DRY,
        ALERT_SOIL_WET,
        ALERT_TEMP_HIGH,
        ALERT_TEMP_LOW,
        IDEAL_AQI_MAX,
        IDEAL_HUM_MAX,
        IDEAL_HUM_MIN,
        IDEAL_SOIL_MAX,
        IDEAL_SOIL_MIN,
        IDEAL_TEMP_MAX,
        IDEAL_TEMP_MIN,
        MAX_SCORE_HISTORY,
        WEIGHT_AQI,
        WEIGHT_HUM,
        WEIGHT_PRES,
        WEIGHT_RAIN,
        WEIGHT_SOIL,
        WEIGHT_TEMP,
    )
except ImportError:
    from config import (
        ALERT_AQI_HIGH,
        ALERT_HUM_LOW,
        ALERT_SOIL_DRY,
        ALERT_SOIL_WET,
        ALERT_TEMP_HIGH,
        ALERT_TEMP_LOW,
        IDEAL_AQI_MAX,
        IDEAL_HUM_MAX,
        IDEAL_HUM_MIN,
        IDEAL_SOIL_MAX,
        IDEAL_SOIL_MIN,
        IDEAL_TEMP_MAX,
        IDEAL_TEMP_MIN,
        MAX_SCORE_HISTORY,
        WEIGHT_AQI,
        WEIGHT_HUM,
        WEIGHT_PRES,
        WEIGHT_RAIN,
        WEIGHT_SOIL,
        WEIGHT_TEMP,
    )


class HealthScorer:
    def __init__(self):
        self.score_history = deque(maxlen=MAX_SCORE_HISTORY)
        print("🩺 Health Scorer ready")

    def _score_temperature(self, temp):
        """Score temperature 0 → WEIGHT_TEMP (30 pts)."""
        if IDEAL_TEMP_MIN <= temp <= IDEAL_TEMP_MAX:
            return WEIGHT_TEMP
        if temp < IDEAL_TEMP_MIN:
            return max(0, WEIGHT_TEMP - (IDEAL_TEMP_MIN - temp) * 2)
        return max(0, WEIGHT_TEMP - (temp - IDEAL_TEMP_MAX) * 2)

    def _score_humidity(self, hum):
        """Score humidity 0 → WEIGHT_HUM (25 pts)."""
        if IDEAL_HUM_MIN <= hum <= IDEAL_HUM_MAX:
            return WEIGHT_HUM
        if hum < IDEAL_HUM_MIN:
            return max(0, WEIGHT_HUM - (IDEAL_HUM_MIN - hum) * 0.5)
        return max(0, WEIGHT_HUM - (hum - IDEAL_HUM_MAX) * 0.3)

    def _score_air_quality(self, aqi):
        """Score AQI 0 → WEIGHT_AQI (15 pts). Lower AQI = better."""
        if aqi <= IDEAL_AQI_MAX:
            return WEIGHT_AQI
        return max(0, WEIGHT_AQI - (aqi - IDEAL_AQI_MAX) / 50)

    def _score_soil_moisture(self, soil):
        """Score soil moisture 0 → WEIGHT_SOIL (20 pts). Ideal: 40–70%."""
        if IDEAL_SOIL_MIN <= soil <= IDEAL_SOIL_MAX:
            return WEIGHT_SOIL
        if soil < IDEAL_SOIL_MIN:
            # Too dry — deduct 0.5pt per % below ideal
            return max(0, WEIGHT_SOIL - (IDEAL_SOIL_MIN - soil) * 0.5)
        # Too wet — deduct 0.4pt per % above ideal
        return max(0, WEIGHT_SOIL - (soil - IDEAL_SOIL_MAX) * 0.4)

    def _score_rain(self, rain):
        """Score rain sensor 0 → WEIGHT_RAIN (15 pts)."""
        return WEIGHT_RAIN if rain == 1 else 8

    def _score_pressure(self, pressure):
        """Score pressure 0 → WEIGHT_PRES (10 pts)."""
        if 1000 <= pressure <= 1020:
            return WEIGHT_PRES
        distance = (1000 - pressure) if pressure < 1000 else (pressure - 1020)
        return max(0, WEIGHT_PRES - distance * 0.5)

    def _check_alerts(self, reading):
        """Detect urgent alert conditions regardless of score."""
        alerts = []
        if reading["temperature"] > ALERT_TEMP_HIGH:
            alerts.append(
                f"🚨 CRITICAL: Temperature {reading['temperature']}°C — heat emergency!"
            )
        if reading["temperature"] < ALERT_TEMP_LOW:
            alerts.append(
                f"🚨 CRITICAL: Temperature {reading['temperature']}°C — dangerously cold!"
            )
        if reading["humidity"] < ALERT_HUM_LOW:
            alerts.append(
                f"🚨 CRITICAL: Humidity {reading['humidity']}% — drought conditions!"
            )
        if reading["air_quality"] > ALERT_AQI_HIGH:
            alerts.append(
                f"🚨 WARNING: Air quality {reading['air_quality']} ppm — poor ventilation!"
            )
        soil = reading.get("soil_moisture", 55)
        if soil < ALERT_SOIL_DRY:
            alerts.append(f"🚨 CRITICAL: Soil {soil}% — plant is drought-stressed!")
        if soil > ALERT_SOIL_WET:
            alerts.append(f"🚨 WARNING: Soil {soil}% — risk of root rot!")
        return alerts

    def calculate_score(self, reading):
        """Calculate full health score for one reading."""
        if reading is None:
            return None

        soil = reading.get("soil_moisture", 55)  # default to healthy if missing

        temp_score = self._score_temperature(reading["temperature"])
        hum_score = self._score_humidity(reading["humidity"])
        aqi_score = self._score_air_quality(reading["air_quality"])
        rain_score = self._score_rain(reading["rain"])
        pres_score = self._score_pressure(reading["pressure"])
        soil_score = self._score_soil_moisture(soil)

        total = round(
            temp_score + hum_score + aqi_score + rain_score + pres_score + soil_score
        )
        total = max(0, min(100, total))

        if total >= 85:
            status = "excellent"
        elif total >= 70:
            status = "good"
        elif total >= 50:
            status = "mild_stress"
        elif total >= 30:
            status = "stressed"
        else:
            status = "critical"

        alerts = self._check_alerts(reading)

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
                "pressure": round(pres_score, 1),
                "soil_moisture": round(soil_score, 1),
            },
        }
        self.score_history.append(result)
        return result

    def get_score_trend(self):
        """Is Luna's health improving or getting worse?"""
        recent = list(self.score_history)
        if len(recent) < 4:
            return "insufficient data"

        mid = len(recent) // 2
        avg_first = sum(r["score"] for r in recent[:mid]) / mid
        avg_second = sum(r["score"] for r in recent[mid:]) / (len(recent) - mid)
        diff = avg_second - avg_first

        if diff > 3:
            return "improving 📈"
        if diff < -3:
            return "declining 📉"
        return "stable ➡️"

    def format_score(self, result):
        """Pretty-print the score result for the terminal."""
        if result is None:
            return "No score calculated"
        score = result["score"]
        indicator = "🟢" if score >= 85 else ("🟡" if score >= 50 else "🔴")
        b = result["breakdown"]
        lines = [
            f"{indicator} Health Score: {score}/100 — {result['status'].upper()}",
            f"   Temp={b['temperature']}pt  Hum={b['humidity']}pt  "
            f"Soil={b['soil_moisture']}pt  AQI={b['air_quality']}pt  "
            f"Rain={b['rain']}pt  Pres={b['pressure']}pt",
            f"   Trend: {self.get_score_trend()}",
        ]
        for alert in result["alerts"]:
            lines.append(f"   {alert}")
        return "\n".join(lines)


if __name__ == "__main__":
    print("🧪 Testing Health Scorer Module\n")
    scorer = HealthScorer()

    scenarios = [
        (
            "Test 1 — Perfect conditions",
            {
                "temperature": 22,
                "humidity": 60,
                "air_quality": 400,
                "rain": 1,
                "pressure": 1013,
                "timestamp": str(datetime.now()),
                "status": "ok",
            },
        ),
        (
            "Test 2 — Stressed plant",
            {
                "temperature": 33,
                "humidity": 25,
                "air_quality": 700,
                "rain": 0,
                "pressure": 1013,
                "timestamp": str(datetime.now()),
                "status": "ok",
            },
        ),
        (
            "Test 3 — Critical emergency",
            {
                "temperature": 40,
                "humidity": 12,
                "air_quality": 1500,
                "rain": 0,
                "pressure": 1013,
                "timestamp": str(datetime.now()),
                "status": "ok",
            },
        ),
    ]

    for label, reading in scenarios:
        print(f"\n{label}:")
        result = scorer.calculate_score(reading)
        print(scorer.format_score(result))

    print(f"\nOverall health trend: {scorer.get_score_trend()}")
    print("\n✅ Health scorer test complete!")
