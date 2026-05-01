import sys, os

# Fix emoji display on Windows PowerShell (sets UTF-8 for this process)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from python.serial_reader import SerialReader
import time


def main():
    print("🌱 Luna — AI Plant Care System")
    print("================================")

    reader=SerialReader(use_simulator=True)
    try:
        while True:
            reading=reader.get_reading()

            if reading is not None:
                print(f"✅ Reading received: {reading['timestamp']} | "
                      f"Temp={reading['temperature']}°C | "
                      f"Hum={reading['humidity']}% | "
                      f"AQI={reading['air_quality']}ppm | "
                      f"Rain={reading['rain']} | "
                      f"Pressure={reading['pressure']}hPa | "
                      f"Status={reading['status']}")
    except KeyboardInterrupt:
        reader.close()
        print("👋 Luna is going to sleep. Goodbye!")        
        
    

if __name__ == "__main__":
    main()
