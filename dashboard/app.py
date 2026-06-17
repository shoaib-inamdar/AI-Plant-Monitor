import sys
import os
import json
import threading

# UTF-8 Fix
sys.stdout.reconfigure(encoding="utf-8")

from flask import Flask, jsonify, render_template

# Add project root to Python path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from python.memory import LunaMemory
from python.config import (
    MEMORY_FILE_PATH,
    CARE_PLAN_FILE,
    INCIDENTS_FILE
)

# Create Flask App
app = Flask(__name__)


# -----------------------------
# Helper: Load JSON Safely
# -----------------------------
def load_json(filepath):
    """
    Read a JSON file and return its contents.
    If file doesn't exist or is invalid, return {}.
    """
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read().strip()

        if not content:
            return {}

        return json.loads(content)

    except Exception:
        return {}


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    """
    Serve Dashboard Page
    """
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """
    Return all current Luna data as JSON.
    """

    memory_data = load_json(MEMORY_FILE_PATH)
    care_plan_data = load_json(CARE_PLAN_FILE)
    incidents_data = load_json(INCIDENTS_FILE)

    readings = memory_data.get("readings", [])
    ai_responses = memory_data.get("ai_responses", [])

    # Latest Reading
    latest = readings[-1] if readings else {}

    # Last AI Response
    last_ai = ai_responses[-1] if ai_responses else {}

    # Recent Scores
    recent_scores = [
        response.get("health_score", 50)
        for response in ai_responses[-20:]
    ]

    return jsonify(
        {
            "latest_reading": latest,
            "last_ai_response": last_ai,
            "recent_scores": recent_scores,
            "care_plan": care_plan_data,
            "incidents": incidents_data.get("incidents", []),
            "daily_summary": memory_data.get(
                "daily_summaries",
                {}
            ),
            "total_readings": len(readings),
        }
    )


@app.route("/api/mark_done/<int:task_index>", methods=["POST"])
def mark_task_done(task_index):
    """
    Mark a care plan task as completed.
    """

    try:
        care_plan = load_json(CARE_PLAN_FILE)

        if not care_plan:
            return jsonify(
                {"error": "No care plan found"}
            ), 404

        tasks = care_plan.get("tasks", [])

        if task_index < 0 or task_index >= len(tasks):
            return jsonify(
                {"error": "Invalid task index"}
            ), 400

        tasks[task_index]["done"] = True

        with open(
            CARE_PLAN_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                care_plan,
                file,
                indent=4,
                ensure_ascii=False
            )

        return jsonify({"success": True})

    except Exception as error:
        return jsonify(
            {"error": str(error)}
        ), 500


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print(
        "🌱 Luna Dashboard starting at "
        "http://localhost:5000"
    )

    app.run(
        debug=False,
        port=5000,
        threaded=True
    )