"""
serial_reader.py
────────────────────────────────────────────────────────────────────────────
Unified sensor interface that handles:
  - Simulated data (USE_REAL_HARDWARE=False)
  - Real Arduino serial (USE_REAL_HARDWARE=True)
  - Per-sensor hardware toggles (HW_DHT22, HW_MQ135, HW_RAIN, HW_BMP280, HW_SOIL)

When a sensor is toggled OFF, its safe default value is used instead.
The output reading dict always has the same keys regardless of which
sensors are active, so all downstream modules (scorer, memory, AI) are
unaffected by missing hardware.
"""

from datetime import datetime

try:
    from python.config import (
        AQI_MAX,
        AQI_MIN,
        BAUD_RATE,
        DEFAULT_AIR_QUALITY,
        DEFAULT_PRESSURE,
        DEFAULT_RAIN,
        DEFAULT_SOIL_MOISTURE,
        HUM_MAX,
        HUM_MIN,
        HW_BMP280_AVAILABLE,
        HW_DHT22_AVAILABLE,
        HW_MQ135_AVAILABLE,
        HW_RAIN_AVAILABLE,
        HW_SOIL_AVAILABLE,
        PRES_MAX,
        PRES_MIN,
        READ_INTERVAL_SECONDS,
        SERIAL_PORT,
        SOIL_MAX,
        SOIL_MIN,
        TEMP_MAX,
        TEMP_MIN,
        USE_REAL_HARDWARE,
    )
    from python.sensor_simulator import SimulatedSerial
except ImportError:
    from config import (
        AQI_MAX,
        AQI_MIN,
        BAUD_RATE,
        DEFAULT_AIR_QUALITY,
        DEFAULT_PRESSURE,
        DEFAULT_RAIN,
        DEFAULT_SOIL_MOISTURE,
        HUM_MAX,
        HUM_MIN,
        HW_BMP280_AVAILABLE,
        HW_DHT22_AVAILABLE,
        HW_MQ135_AVAILABLE,
        HW_RAIN_AVAILABLE,
        HW_SOIL_AVAILABLE,
        PRES_MAX,
        PRES_MIN,
        SERIAL_PORT,
        SOIL_MAX,
        SOIL_MIN,
        TEMP_MAX,
        TEMP_MIN,
        USE_REAL_HARDWARE,
    )
    from sensor_simulator import SimulatedSerial

try:
    from serial import SerialException
except ImportError:
    SerialException = Exception  # fallback if pyserial not installed


# ── SERIAL READER ─────────────────────────────────────────────────────────────
class SerialReader:
    """
    Unified sensor reader.

    use_simulator parameter is OVERRIDDEN by config.USE_REAL_HARDWARE.
    Leave use_simulator=True in main.py — hardware is controlled via config.py.
    """

    def __init__(self, use_simulator=True):
        # Config takes priority over the parameter
        use_sim = not USE_REAL_HARDWARE

        self._print_hardware_status()

        if use_sim:
            self.serial = SimulatedSerial()
            self.mode = "simulator"
            print("📡 Mode: Sensor Simulator")
        else:
            try:
                import serial

                self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                self.mode = "hardware"
                print(f"📡 Mode: Real ESP32 on {SERIAL_PORT}")
            except (SerialException, Exception) as e:
                print(f"❌ Could not open {SERIAL_PORT}: {e}")
                print("   Falling back to simulator.")
                self.serial = SimulatedSerial()
                self.mode = "simulator_fallback"

        self.last_reading = None

    def _print_hardware_status(self):
        """Print a clear hardware toggle status table at startup."""
        if USE_REAL_HARDWARE:
            print("\n🔌 Hardware Mode: REAL ESP32")
            sensors = [
                 ("DHT22 (Temp+Hum)", HW_DHT22_AVAILABLE, "GPIO 4"),
                  ("MQ-135 (Air)", HW_MQ135_AVAILABLE, "GPIO 32"),
                 ("Rain Sensor", HW_RAIN_AVAILABLE, "GPIO 27"),
                  ("BMP280 (Pressure)", HW_BMP280_AVAILABLE, "I2C GPIO 21/22"),
                  ("Soil Moisture", HW_SOIL_AVAILABLE, "GPIO 34"),
                ]
            for name, avail, pin in sensors:
                status = "✅ ACTIVE" if avail else "⬜ OFF (default value used)"
                print(f"   {name:<22} {status}  ({pin})")
            print()
        else:
            print("📡 Hardware Mode: SIMULATOR (USE_REAL_HARDWARE=False in config.py)")

    # ── READING FROM SERIAL ────────────────────────────────────────────────────

    def read_raw_line(self):
        if not self.serial.is_open:
            return None
        try:
            raw = self.serial.readline().decode("utf-8").strip()
            # Skip Arduino comment lines (start with #)
            if raw.startswith("#") or not raw:
                return None
            return raw
        except Exception as error:
            print(f"⚠️  Serial read error: {error}")
            return None

    def parse_line(self, raw_line):
        """
        Parse a key:value CSV line from the Arduino or simulator.
        Format: TEMP:24.3,HUM:62.1,AIR:450,RAIN:0,PRES:1013.50,SOIL:55.0

        Missing fields are filled with safe defaults based on hardware toggles.
        """
        try:
            data = {}
            for part in raw_line.split(","):
                if ":" not in part:
                    continue
                key, value = part.split(":", 1)
                data[key.strip()] = value.strip()

            # ── Temperature + Humidity (DHT22) ────────────────────────────
            if HW_DHT22_AVAILABLE or self.mode.startswith("sim"):
                temperature = float(data["TEMP"])
                humidity = float(data["HUM"])
            else:
                # Sensor off — but we still need some value; use last known or 25°C
                prev = self.last_reading or {}
                temperature = prev.get("temperature", 25.0)
                humidity = prev.get("humidity", 60.0)

            # ── Air Quality (MQ-135) ──────────────────────────────────────
            if HW_MQ135_AVAILABLE or self.mode.startswith("sim"):
                air_quality = int(data["AIR"])
            else:
                air_quality = DEFAULT_AIR_QUALITY

            # ── Rain sensor ───────────────────────────────────────────────
            if HW_RAIN_AVAILABLE or self.mode.startswith("sim"):
                rain = int(data["RAIN"])
            else:
                rain = DEFAULT_RAIN

            # ── Barometric pressure (BMP280) ──────────────────────────────
            if HW_BMP280_AVAILABLE or self.mode.startswith("sim"):
                pressure = float(data["PRES"])
            else:
                pressure = DEFAULT_PRESSURE

            # ── Soil moisture ─────────────────────────────────────────────
            if HW_SOIL_AVAILABLE or self.mode.startswith("sim"):
                soil_moisture = float(data.get("SOIL", DEFAULT_SOIL_MOISTURE))
            else:
                soil_moisture = DEFAULT_SOIL_MOISTURE

            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": temperature,
                "humidity": humidity,
                "air_quality": air_quality,
                "rain": rain,
                "pressure": pressure,
                "soil_moisture": soil_moisture,
            }

        except Exception as error:
            print(f"⚠️  Parse error on '{raw_line}': {error}")
            return None

    def validate_reading(self, reading):
        """Validate ranges. Sets status='error' on out-of-range values."""
        if reading is None:
            return None

        status = "ok"
        checks = [
            ("temperature", reading["temperature"], TEMP_MIN, TEMP_MAX),
            ("humidity", reading["humidity"], HUM_MIN, HUM_MAX),
            ("air_quality", reading["air_quality"], AQI_MIN, AQI_MAX),
            ("pressure", reading["pressure"], PRES_MIN, PRES_MAX),
            ("soil_moisture", reading["soil_moisture"], SOIL_MIN, SOIL_MAX),
        ]
        for field, value, lo, hi in checks:
            if not (lo <= value <= hi):
                print(f"⚠️  {field} out of range: {value} (expected {lo}–{hi})")
                status = "error"

        if reading["rain"] not in (0, 1):
            print(f"⚠️  Invalid rain value: {reading['rain']}")
            status = "error"

        reading["status"] = status
        return reading

    def get_reading(self):
        raw = self.read_raw_line()
        if raw is None:
            return None
        parsed = self.parse_line(raw)
        if parsed is None:
            return None
        validated = self.validate_reading(parsed)
        if validated is not None:
            self.last_reading = validated
        return validated

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        print("📡 Serial reader closed")


# ── STANDALONE TEST ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    reader = SerialReader(use_simulator=True)
    print("\nStreaming 5 readings — press Ctrl+C to stop\n")
    try:
        for i in range(5):
            reading = reader.get_reading()
            if reading:
                print(
                    f"[{reading['timestamp']}] "
                    f"Temp={reading['temperature']}°C  "
                    f"Hum={reading['humidity']}%  "
                    f"Soil={reading['soil_moisture']}%  "
                    f"AQI={reading['air_quality']}ppm  "
                    f"Rain={'🌧' if reading['rain'] else '☀'}  "
                    f"Pres={reading['pressure']}hPa  "
                    f"Status={reading['status']}"
                )
    except KeyboardInterrupt:
        pass
    finally:
        reader.close()
