import json
import os
import sys

# UTF-8 fix
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, jsonify, render_template

# ── Path setup ────────────────────────────────────────────────────────────────
# Anchor all imports and file paths to project root regardless of launch dir
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from python.config import (
    CARE_PLAN_FILE,
    INCIDENTS_FILE,
    MEMORY_FILE_PATH,
    USE_REAL_HARDWARE,
)


# Resolve relative config paths to absolute
def _abs(p):
    return os.path.join(_PROJECT_ROOT, p)


MEMORY_FILE = _abs(MEMORY_FILE_PATH)
CARE_PLAN = _abs(CARE_PLAN_FILE)
INCIDENTS = _abs(INCIDENTS_FILE)

app = Flask(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_json(filepath):
    """Read a JSON file. Returns {} if missing, empty, or invalid."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read().strip()
        return json.loads(content) if content else {}
    except Exception:
        return {}


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    memory_data = load_json(MEMORY_FILE)
    care_plan_data = load_json(CARE_PLAN)
    incidents_data = load_json(INCIDENTS)

    readings = memory_data.get("readings", [])
    ai_responses = memory_data.get("ai_responses", [])

    latest = readings[-1] if readings else {}
    last_ai = ai_responses[-1] if ai_responses else {}

    # Last 40 AI scores for the chart
    recent_scores = [r.get("health_score", 50) for r in ai_responses[-40:]]

    return jsonify(
        {
            "latest_reading": latest,
            "last_ai_response": last_ai,
            "recent_scores": recent_scores,
            "care_plan": care_plan_data,
            "incidents": incidents_data.get("incidents", []),
            "daily_summary": memory_data.get("daily_summaries", {}),
            "total_readings": len(readings),
            "mode": "hardware" if USE_REAL_HARDWARE else "simulator",
        }
    )


@app.route("/api/mark_done/<int:task_index>", methods=["POST"])
def mark_task_done(task_index):
    try:
        care_plan = load_json(CARE_PLAN)
        if not care_plan:
            return jsonify({"error": "No care plan found"}), 404

        tasks = care_plan.get("tasks", [])
        if task_index < 0 or task_index >= len(tasks):
            return jsonify({"error": "Invalid task index"}), 400

        tasks[task_index]["done"] = True
        with open(CARE_PLAN, "w", encoding="utf-8") as f:
            json.dump(care_plan, f, indent=2, ensure_ascii=False)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def api_health():
    """Simple health check endpoint."""
    return jsonify(
        {"status": "ok", "mode": "hardware" if USE_REAL_HARDWARE else "simulator"}
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = "REAL HARDWARE" if USE_REAL_HARDWARE else "SIMULATOR"
    print(f"🌱 Luna Dashboard → http://localhost:5000  [{mode}]")
    app.run(debug=False, port=5000, threaded=True)
