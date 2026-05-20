import sys
import os
import json
import time

# UTF-8 fix (must be first)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from datetime import datetime

try:
    from python.config import (
        CARE_PLAN_FILE, AI_MODEL, GEMINI_API_KEY,
        MORNING_START, MORNING_END, AFTERNOON_START, AFTERNOON_END,
        EVENING_START, EVENING_END, MAX_RETRIES
    )
except ImportError:
    from config import (
        CARE_PLAN_FILE, AI_MODEL, GEMINI_API_KEY,
        MORNING_START, MORNING_END, AFTERNOON_START, AFTERNOON_END,
        EVENING_START, EVENING_END, MAX_RETRIES
    )

import google.genai as genai

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
# BUG FIX 1: Prompt used single quotes inside the JSON template, which is
# invalid JSON. Replaced with double-quotes or backtick-style description.
CARE_PLAN_SYSTEM_PROMPT = """
You are Luna, a wise plant who plans her own care for the day.

You will receive a summary of your recent health and sensor history.
Generate a practical, specific care plan for today.

Respond with ONLY valid JSON in this exact format (no markdown, no explanation):
{
  "date": "YYYY-MM-DD",
  "summary": "1-2 sentences about today's focus",
  "tasks": [
    {
      "time": "morning",
      "action": "specific action to take",
      "priority": "high",
      "done": false
    }
  ]
}

Rules:
- "time" must be exactly "morning", "afternoon", or "evening"
- "priority" must be exactly "high", "medium", or "low"
- Include 2-3 tasks per time period (6-9 tasks total)
- Base advice on the health summary provided
- Be specific (e.g. "give 200ml of water at the base", not just "water plant")
"""


# ── CLASS: Scheduler ──────────────────────────────────────────────────────────
class Scheduler:
    def __init__(self, memory):
        self.memory = memory
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.today_plan = None

        self._load_plan()
        print("📅 Scheduler ready")

    # ── LOAD ──────────────────────────────────────────────────────────────────
    def _load_plan(self):
        """Load today's plan from disk if it exists."""

        if not os.path.exists(CARE_PLAN_FILE):
            return

        try:
            # BUG FIX 2: `try` was missing its colon → SyntaxError
            # BUG FIX 3: `json(file)` is not valid — must be `json.load(file)`
            with open(CARE_PLAN_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if not content:
                    return
                parsed = json.loads(content)

            today = datetime.now().strftime("%Y-%m-%d")
            if parsed.get("date") == today:
                self.today_plan = parsed
                # BUG FIX 4: `tasks` variable was undefined — must access via parsed
                task_count = len(parsed.get("tasks", []))
                print(f"📅 Loaded today's care plan ({task_count} tasks)")
            else:
                print("📅 Old plan found — will generate new one")
                self.today_plan = None

        except Exception as error:
            print(f"⚠️ Could not load care plan: {error}")
            self.today_plan = None

    # ── SAVE ──────────────────────────────────────────────────────────────────
    def _save_plan(self):
        """Save current plan to disk."""

        # BUG FIX 5: `os.makedirs()` returns None, not a boolean.
        # The `if os.makedirs(...)` condition always evaluates to False,
        # so the file was NEVER being written. Run makedirs separately.
        folder = os.path.dirname(CARE_PLAN_FILE)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(CARE_PLAN_FILE, "w", encoding="utf-8") as file:
            json.dump(self.today_plan, file, indent=2)

    # ── GENERATE ──────────────────────────────────────────────────────────────
    def generate_plan(self):
        """Ask Gemini to create today's care plan using memory data."""

        summary_text = self.memory.get_summary_text()
        today_daily = self.memory.get_daily_summary()
        today_date = datetime.now().strftime("%Y-%m-%d")

        context = f"Health memory summary:\n{summary_text}\n"

        if today_daily is not None:
            # BUG FIX 6: `today_date` was used but never defined in original code
            context += (
                f"\nToday's averages ({today_date}):\n"
                f"- Avg temp: {today_daily['avg_temperature']}°C\n"
                f"- Avg humidity: {today_daily['avg_humidity']}%\n"
                f"- Rain events: {today_daily['rain_events']}\n"
            )

        context += f"\nToday is {today_date}. Generate a care plan for today."
        full_prompt = CARE_PLAN_SYSTEM_PROMPT + "\n\n" + context

        for attempt in range(MAX_RETRIES):
            try:
                # BUG FIX 7: `generate_cotent` is a typo → `generate_content`
                # BUG FIX 8: first arg must be keyword `model=`, not positional
                response = self.client.models.generate_content(
                    model=AI_MODEL,
                    contents=full_prompt
                )

                # BUG FIX 9: `response.summary_text` doesn't exist → `response.text`
                response_text = response.text.strip()

                # Strip ```json markdown wrapper if present
                if response_text.startswith("```"):
                    lines = response_text.splitlines()
                    if len(lines) >= 2:
                        lines = lines[1:-1]
                    response_text = "\n".join(lines).strip()

                parsed = json.loads(response_text)

                # Validate required fields
                for field in ["date", "tasks", "summary"]:
                    if field not in parsed:
                        raise ValueError(f"Missing field: {field}")

                if not isinstance(parsed["tasks"], list):
                    raise ValueError("Field 'tasks' must be a list")

                # Ensure every task has a "done" field
                for task in parsed["tasks"]:
                    task.setdefault("done", False)

                self.today_plan = parsed
                self._save_plan()

                # BUG FIX 10: `tasks` was undefined — use parsed["tasks"]
                print(f"📅 Care plan generated: {len(parsed['tasks'])} tasks for today")
                return parsed

            except json.JSONDecodeError:
                print(f"⚠️ Attempt {attempt + 1}: Gemini returned invalid JSON. Retrying...")
                time.sleep(1)

            except Exception as error:
                print(f"⚠️ Plan generation error (attempt {attempt + 1}): {error}")
                time.sleep(2)

        print("❌ Could not generate care plan after all retries.")
        return None

    # ── DUE TASKS ─────────────────────────────────────────────────────────────
    def get_due_tasks(self):
        """Return incomplete tasks scheduled for the current time window."""

        if self.today_plan is None or "tasks" not in self.today_plan:
            return []

        current_hour = datetime.now().hour

        if MORNING_START <= current_hour < MORNING_END:
            current_period = "morning"
        elif AFTERNOON_START <= current_hour < AFTERNOON_END:
            current_period = "afternoon"
        elif EVENING_START <= current_hour < EVENING_END:
            current_period = "evening"
        else:
            current_period = None

        if current_period is None:
            return []

        # BUG FIX 11: condition was `task.get("done", False)` — this returns
        # tasks that ARE done (truthy), not ones that are NOT done.
        # Should be `not task.get("done", False)`.
        return [
            task for task in self.today_plan["tasks"]
            if task.get("time") == current_period and not task.get("done", False)
        ]

    # ── MARK DONE ─────────────────────────────────────────────────────────────
    def mark_task_done(self, task_index):
        """Mark a specific task as completed."""

        if self.today_plan is None:
            return

        try:
            self.today_plan["tasks"][task_index]["done"] = True
            self._save_plan()
            action = self.today_plan["tasks"][task_index]["action"]
            print(f"✅ Task done: {action}")

        except IndexError:
            print(f"⚠️ No task at index {task_index}")

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    def get_plan_summary(self):
        """Return a human-readable summary of today's plan."""

        # This method was entirely missing — written from scratch
        if self.today_plan is None:
            return "📅 No care plan for today yet."

        tasks = self.today_plan["tasks"]
        done_count = sum(1 for t in tasks if t.get("done", False))
        total_count = len(tasks)
        today_date = self.today_plan.get("date", "today")
        plan_summary = self.today_plan.get("summary", "")

        def format_tasks(period):
            period_tasks = [t for t in tasks if t.get("time") == period]
            if not period_tasks:
                return "  (none)\n"
            lines = ""
            for t in period_tasks:
                icon = "✅" if t.get("done", False) else "🔲"
                priority = t.get("priority", "medium")
                lines += f"  {icon} [{priority.upper()}] {t['action']}\n"
            return lines

        return (
            f"📅 Today's Care Plan ({today_date}):\n"
            f"   {plan_summary}\n\n"
            f"   Progress: {done_count}/{total_count} tasks done\n\n"
            f"🌅 Morning:\n{format_tasks('morning')}\n"
            f"🌞 Afternoon:\n{format_tasks('afternoon')}\n"
            f"🌙 Evening:\n{format_tasks('evening')}"
        )


# ── STANDALONE TEST ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Import memory here so this file is self-contained when run directly
    try:
        from python.memory import LunaMemory
    except ImportError:
        from memory import LunaMemory

    print("🧪 Testing Scheduler Module\n")

    memory = LunaMemory()
    scheduler = Scheduler(memory)

    print("\nGenerating today's care plan (calling Gemini)...")
    plan = scheduler.generate_plan()

    if plan:
        print()
        print(scheduler.get_plan_summary())

        print("\nDue tasks right now:")
        due = scheduler.get_due_tasks()
        if due:
            for i, task in enumerate(due):
                print(f"  [{i}] {task['action']} (Priority: {task['priority']})")
        else:
            print("  No tasks due in the current time window (outside scheduled hours)")
    else:
        print("❌ Plan generation failed.")

    print("\n✅ Scheduler test complete! Check data/care_plan.json")
