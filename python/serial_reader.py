import time
from datetime import datetime

try:
    from python.config import (
        AQI_MAX,
        AQI_MIN,
        BAUD_RATE,
        HUM_MAX,
        HUM_MIN,
        PRES_MAX,
        PRES_MIN,
        READ_INTERVAL_SECONDS,
        SERIAL_PORT,
        TEMP_MAX,
        TEMP_MIN,
    )
    from python.sensor_simulator import SimulatedSerial
except ImportError:
    from config import (
        AQI_MAX,
        AQI_MIN,
        BAUD_RATE,
        HUM_MAX,
        HUM_MIN,
        PRES_MAX,
        PRES_MIN,
        READ_INTERVAL_SECONDS,
        SERIAL_PORT,
        TEMP_MAX,
        TEMP_MIN,
    )
    from sensor_simulator import SimulatedSerial

try:
    from serial import SerialException
except ImportError:
    SerialException = Exception  # fallback if pyserial not installed


class SerialReader:
    def __init__(self, use_simulator=True):

        if use_simulator:
            self.serial = SimulatedSerial()
            print("📡 Using simulated sensor data")
        else:
            try:
                import serial

                self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                print(f"📡 Connected to real Arduino on {SERIAL_PORT}")

            except SerialException:
                print(f"❌ Failed to open {SERIAL_PORT}\nFalling back to simulator.")

        self.last_reading = None

    def read_raw_line(self):
        if not self.serial.is_open:
            return None

        try:
            raw_line = self.serial.readline().decode("utf-8").strip()
            if not raw_line:
                return None
            else:
                return raw_line
        except Exception as error:
            print(f"⚠️ Error reading serial line: {error}")

    def parse_line(self, raw_line):
        try:
            parts = raw_line.split(",")

            data = {}
            for p in parts:
                if ":" not in p:
                    continue

                key, value = p.split(":", 1)  # ✅ FIXED
                key = key.strip()
                value = value.strip()

                data[key] = value

            temperature = float(data["TEMP"])
            humidity = float(data["HUM"])
            air_quality = int(data["AIR"])
            rain = int(data["RAIN"])
            pressure = float(data["PRES"])

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            reading = {
                "timestamp": timestamp,
                "temperature": temperature,
                "humidity": humidity,
                "air_quality": air_quality,
                "rain": rain,
                "pressure": pressure,
            }

            return reading  # ✅ IMPORTANT

        except Exception as error:
            print(f"⚠️ Failed to parse line: '{raw_line}' — {error}")
            return None

    def validate_reading(self, reading):
        if reading is None:
            return None

        status = "ok"

        try:
            if not (TEMP_MIN <= reading["temperature"] <= TEMP_MAX):
                print(f"⚠️ Temperature out of range: {reading['temperature']}")
                status = "error"

            if not (HUM_MIN <= reading["humidity"] <= HUM_MAX):
                print(f"⚠️ Humidity out of range: {reading['humidity']}")
                status = "error"

            if not (AQI_MIN <= reading["air_quality"] <= AQI_MAX):
                print(f"⚠️ Air quality out of range: {reading['air_quality']}")
                status = "error"

            if not (PRES_MIN <= reading["pressure"] <= PRES_MAX):
                print(f"⚠️ Pressure out of range: {reading['pressure']}")
                status = "error"

            if reading["rain"] not in (0, 1):
                print(f"⚠️ Invalid rain value: {reading['rain']}")
                status = "error"

            reading["status"] = status
            return reading

        except Exception as error:
            print(f"⚠️ Validation error: {error}")
            reading["status"] = "error"
            return reading

    def get_reading(self):
        raw_line = self.read_raw_line()
        if raw_line is None:
            return None

        parsed = self.parse_line(raw_line)
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


if __name__ == "__main__":
    reader = SerialReader(use_simulator=True)
    try:
        while True:
            reading = reader.get_reading()

            if reading is not None:
                print(f"[{reading['timestamp']}] Status: {reading['status']}")
                print(f"  🌡️  Temp: {reading['temperature']}°C")
                print(f"  💧  Hum: {reading['humidity']}%")
                print(f"  🌫️  AQI: {reading['air_quality']}ppm")
                print(f"  ⛲  Rain: {'Yes' if reading['rain'] == 1 else 'No'}")
                print(f"  🧭  Pressure: {reading['pressure']}hPa")
                print()
            else:
                print("⚠️ No reading received")
            time.sleep(READ_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n🚫 Program interrupted by user")

    finally:
        reader.close()
