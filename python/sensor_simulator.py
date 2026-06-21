"""
sensor_simulator.py
────────────────────────────────────────────────────────────────────────────
Realistic plant environment simulator for Luna.

Produces data that follows real diurnal patterns:
  - Temperature peaks 12–16h (hottest part of day)
  - Humidity inversely tracks temperature
  - Soil moisture dries slowly over 24h then "rain event" resets it
  - AQI worsens slightly during day (ventilation patterns)
  - Rain is rare (≈8% chance per cycle)
  - Pressure drifts slowly around 1013 hPa

Includes soil moisture (the most important plant health signal).
CSV format: TEMP,HUM,AIR,RAIN,PRES,SOIL
"""

import csv
import math
import os
import random
import time
from datetime import datetime

try:
    from python.config import CSV_LOG_PATH, DEFAULT_SOIL_MOISTURE
except ImportError:
    from config import CSV_LOG_PATH, DEFAULT_SOIL_MOISTURE


# ── SOIL MOISTURE STATE ───────────────────────────────────────────────────────
# Soil moisture is stateful — it dries out slowly across time
_soil_moisture = DEFAULT_SOIL_MOISTURE   # start at healthy level
_last_soil_update = time.time()

# ── PRESSURE DRIFT ────────────────────────────────────────────────────────────
_pressure_base = 1013.25
_pressure_drift = 0.0


def _update_soil():
    """
    Soil dries ~1% per hour (0.0003% per 2-second cycle).
    A rain event resets it to 70-85%. Manual watering also resets.
    """
    global _soil_moisture, _last_soil_update
    now = time.time()
    elapsed = now - _last_soil_update
    _last_soil_update = now

    # Drying rate: ~1% per hour = 0.000278% per second
    dry_rate = 0.000278 * elapsed
    _soil_moisture -= dry_rate

    # Add small noise (sensor jitter)
    _soil_moisture += random.uniform(-0.3, 0.3)

    # Clamp
    _soil_moisture = max(5.0, min(100.0, _soil_moisture))
    return round(_soil_moisture, 1)


def _update_pressure():
    """Pressure drifts slowly ±10 hPa over hours, with small noise."""
    global _pressure_drift
    _pressure_drift += random.uniform(-0.1, 0.1)
    _pressure_drift = max(-8.0, min(8.0, _pressure_drift))  # clamp drift
    pressure = _pressure_base + _pressure_drift + random.uniform(-0.5, 0.5)
    return round(pressure, 2)


def generate_sensor_reading():
    """
    Generate one realistic sensor reading based on current time of day.
    Uses sinusoidal temperature curve (peaks at 14:00, troughs at 04:00).
    """
    global _soil_moisture

    now  = datetime.now()
    hour = now.hour + now.minute / 60.0   # fractional hour

    # ── Temperature: sinusoidal diurnal pattern ────────────────────────────
    # Peak ~14:00, trough ~04:00. Range 18–32°C (typical indoor plant env.)
    base_temp = 25.0
    amplitude = 5.0   # ±5°C swing
    # phase shift: max at hour=14 → sin peaks at π/2 → offset by 14h
    phase = (hour - 14) / 24 * 2 * math.pi
    temperature = base_temp + amplitude * math.sin(phase) + random.uniform(-0.5, 0.5)
    temperature = round(max(15.0, min(40.0, temperature)), 1)

    # ── Humidity: inversely correlated with temperature ────────────────────
    base_humidity = 62.0
    hum_swing = -(temperature - base_temp) * 1.2   # warmer → drier
    humidity = base_humidity + hum_swing + random.uniform(-3, 3)
    humidity = round(max(20.0, min(95.0, humidity)), 1)

    # ── Air quality: slightly worse during day (less ventilation indoors) ──
    base_aqi = 420
    day_factor = max(0, math.sin(phase + math.pi / 4)) * 60
    aqi = int(base_aqi + day_factor + random.randint(-50, 50))
    aqi = max(200, min(1200, aqi))

    # ── Rain: 8% chance per cycle ──────────────────────────────────────────
    rain = 1 if random.random() < 0.08 else 0

    # ── Soil moisture: stateful drying, resets on rain ────────────────────
    soil = _update_soil()
    if rain == 1:
        # Rain event soaks the soil
        _soil_moisture = min(100.0, _soil_moisture + random.uniform(15, 25))
        soil = round(_soil_moisture, 1)

    # ── Pressure: slow drift ──────────────────────────────────────────────
    pressure = _update_pressure()

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "timestamp":    timestamp,
        "temperature":  temperature,
        "humidity":     humidity,
        "air_quality":  aqi,
        "rain":         rain,
        "pressure":     pressure,
        "soil_moisture": soil,
    }


def reading_to_serial_string(reading):
    """
    Format reading as CSV string — must match Arduino output format.
    Format: TEMP:x,HUM:x,AIR:x,RAIN:x,PRES:x,SOIL:x
    """
    return (
        f"TEMP:{reading['temperature']},"
        f"HUM:{reading['humidity']},"
        f"AIR:{reading['air_quality']},"
        f"RAIN:{reading['rain']},"
        f"PRES:{reading['pressure']:.2f},"
        f"SOIL:{reading['soil_moisture']}"
    )


def save_to_csv(reading):
    """Append one reading to the CSV log file."""
    folder = os.path.dirname(CSV_LOG_PATH)
    os.makedirs(folder, exist_ok=True)

    fieldnames = ["timestamp", "temperature", "humidity",
                  "air_quality", "rain", "pressure", "soil_moisture"]

    file_exists = os.path.isfile(CSV_LOG_PATH)
    with open(CSV_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        # Only write fields in fieldnames (ignore extras like 'status')
        writer.writerow({k: reading.get(k, "") for k in fieldnames})


# ── SIMULATED SERIAL PORT ─────────────────────────────────────────────────────
class SimulatedSerial:
    """
    Mimics pyserial's Serial interface.
    readline() returns a bytes-encoded CSV sensor string every 2 seconds.
    """

    def __init__(self, port="SIMULATED", baudrate=9600):
        self.port     = port
        self.baudrate = baudrate
        self.is_open  = True
        print(f"🌱 Simulated serial port active on '{self.port}'")
        print("   Producing realistic diurnal sensor data with soil moisture")

    def readline(self):
        if not self.is_open:
            return b""
        reading      = generate_sensor_reading()
        save_to_csv(reading)
        serial_str   = reading_to_serial_string(reading) + "\n"
        time.sleep(2)   # mimic hardware 2-second cycle
        return serial_str.encode("utf-8")

    def close(self):
        self.is_open = False
        print("🔌 Simulated serial port closed")


# ── STANDALONE TEST ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    s = SimulatedSerial()
    print("\nStreaming simulator output — press Ctrl+C to stop\n")
    try:
        for i in range(10):
            raw   = s.readline().decode("utf-8").strip()
            parts = dict(p.split(":") for p in raw.split(","))
            print(
                f"[{i+1:02d}] Temp={parts['TEMP']}°C  "
                f"Hum={parts['HUM']}%  "
                f"AQI={parts['AIR']}ppm  "
                f"Soil={parts['SOIL']}%  "
                f"Rain={'🌧' if parts['RAIN']=='1' else '☀'}  "
                f"Pres={parts['PRES']}hPa"
            )
    except KeyboardInterrupt:
        s.close()
    print("\n✅ Simulator test complete — check data/sensor_logs/sensor_data.csv")
