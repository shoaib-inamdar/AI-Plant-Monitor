import sys

# Fix emoji display FIRST
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import time

from python.voice_agent import LunaVoice
from python.config import AI_CALL_INTERVAL
from python.ai_brain import LunaBrain
from python.serial_reader import SerialReader
from python.memory import LunaMemory


def main():
    print("🌱 Luna — AI Plant Care System")
    print("================================")

    reader = SerialReader(use_simulator=True)
    brain = LunaBrain()
    voice = LunaVoice()
    memory=LunaMemory()

    print("🌱 Luna is awake and listening to her senses...")

    reading_count = 0
    last_ai_call_time = 0

    try:
        while True:
            reading = reader.get_reading()
            reading_count += 1

            if reading is not None:
                memory.add_reading(reading)
                print(f"📡 Reading #{reading_count}: Temp={reading['temperature']}°C, Hum={reading['humidity']}%")

                current_time = time.time()
                time_since_last_call = current_time - last_ai_call_time

                if time_since_last_call >= AI_CALL_INTERVAL:
                    print("🧠 Asking Luna what she thinks...")

                    response = brain.analyse(reading)

                    if response is not None:
                        memory.add_ai_response(response)

                        if reading_count%5==0:
                            print(memory.get_summary_text())
                            
                        print(brain.format_response(response))
                        voice.speak_response(response)
                        last_ai_call_time = current_time
            else:
                print("⚠️ No reading this cycle")

    except KeyboardInterrupt:
        reader.close()
        print("👋 Luna is going to sleep. Goodbye!")


if __name__ == "__main__":
    main()