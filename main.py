import sys
from python.healer import SelfHealer
# Fix emoji display FIRST
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import time

from python.ai_brain import LunaBrain
from python.config import AI_CALL_INTERVAL
from python.health_scorer import HealthScorer
from python.memory import LunaMemory
from python.scheduler import Scheduler
from python.serial_reader import SerialReader
from python.voice_agent import LunaVoice


def main():
    print("🌱 Luna — AI Plant Care System")
    print("================================")

    reader = SerialReader(use_simulator=True)
    brain = LunaBrain()
    voice = LunaVoice()
    memory = LunaMemory()
    scorer = HealthScorer()
    scheduler = Scheduler(memory)

    # Generate (or load) today's care plan at startup
    if scheduler.today_plan is None:
        print("📅 Generating today's care plan...")
        scheduler.generate_plan()
    print(scheduler.get_plan_summary())
    print()

    print("🌱 Luna is awake and listening to her senses...")

    reading_count = 0
    last_ai_call_time = 0

    try:
        while True:
            reading = reader.get_reading()
            reading_count += 1

            if reading is not None:
                memory.add_reading(reading)
                score_result = scorer.calculate_score(reading)
                if score_result is not None:
                    print(scorer.format_score(score_result))
                    for alert in score_result["alerts"]:
                        print(alert)
                        voice.speak(alert)

                # Check for due tasks every 10 readings
                if reading_count % 10 == 0:
                    due_tasks = scheduler.get_due_tasks()
                    if due_tasks:
                        print(f"📅 {len(due_tasks)} care task(s) due now:")
                        for task in due_tasks:
                            print(f"   → [{task['priority'].upper()}] {task['action']}")
                        voice.speak(f"Reminder: {due_tasks[0]['action']}")

                print(
                    f"📡 Reading #{reading_count}: Temp={reading['temperature']}°C, Hum={reading['humidity']}%"
                )

                current_time = time.time()
                time_since_last_call = current_time - last_ai_call_time

                if time_since_last_call >= AI_CALL_INTERVAL:
                    print("🧠 Asking Luna what she thinks...")

                    # Enrich reading with rule-based score so Gemini has context
                    enriched = reading.copy()
                    if score_result is not None:
                        enriched["rule_based_score"] = score_result["score"]
                        enriched["rule_based_status"] = score_result["status"]

                    response = brain.analyse(enriched)

                    if response is not None:
                        memory.add_ai_response(response)

                        if reading_count % 5 == 0:
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
