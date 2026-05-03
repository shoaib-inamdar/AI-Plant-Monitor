import sys, os

# Fix emoji display on Windows PowerShell — MUST be before any other imports
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from python.config import AI_CALL_INTERVAL
from python.ai_brain import LunaBrain
from python.serial_reader import SerialReader
import time


def main():
    print("🌱 Luna — AI Plant Care System")
    print("================================")

    reader=SerialReader(use_simulator=True)
    brain=LunaBrain()
    print("🌱 Luna is awake and listening to her senses...")
    reading_count=0
    last_ai_call_time=0
    try:
        while True:
            reading=reader.get_reading()
            reading_count+=1

            if reading is not None:
                print(f"📡 Reading #{reading_count}: Temp={reading['temperature']}°C, Hum={reading['humidity']}%")

                current_time=time.time()
                time_since_last_call=current_time-last_ai_call_time

                if time_since_last_call>=AI_CALL_INTERVAL:
                    print("🧠 Asking Luna what she thinks...")
                    response=brain.analyse(reading)

                    if response is not None:
                        print(brain.format_response(response))
                        last_ai_call_time=current_time
            else:
                print("⚠️ No reading this cycle")

    except KeyboardInterrupt:
        reader.close()
        print("👋 Luna is going to sleep. Goodbye!")        
        
    

if __name__ == "__main__":
    main()
