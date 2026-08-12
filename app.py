from flask import Flask, render_template, request, redirect, url_for, jsonify
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)
DATA_FILE = Path(__file__).resolve().parent / "data" / "feedback.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def read_feedback():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return []


def save_feedback(entries):
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2, ensure_ascii=False)


def create_feedback_entry(source):
    return {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "candidate_name": source.get("candidate_name", "").strip(),
        "interviewer_name": source.get("interviewer_name", "").strip(),
        "interview_date": source.get("interview_date", "").strip(),
        "position": source.get("position", "").strip(),
        "rating": source.get("rating", "").strip(),
        "feedback": source.get("feedback", "").strip(),
        "submitted_at": datetime.utcnow().isoformat() + "Z",
    }


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    entries = read_feedback()
    return render_template("dashboard.html", feedback_items=list(reversed(entries)))


@app.route("/feedback", methods=["GET", "POST"])
def feedback_form():
    if request.method == "POST":
        entry = create_feedback_entry(request.form)
        entries = read_feedback()
        entries.append(entry)
        save_feedback(entries)
        return redirect(url_for("feedback_list"))
    return render_template("feedback.html")


@app.route("/feedback/list")
def feedback_list():
    entries = read_feedback()
    return render_template("list.html", feedback_items=list(reversed(entries)))


@app.route("/api/feedback", methods=["GET"])
def api_feedback():
    return jsonify(read_feedback())


@app.route("/api/feedback", methods=["POST"])
def api_add_feedback():
    payload = request.get_json(silent=True) or {}
    if not payload.get("candidate_name"):
        return jsonify({"error": "candidate_name is required"}), 400
    entry = create_feedback_entry(payload)
    entries = read_feedback()
    entries.append(entry)
    save_feedback(entries)
    return jsonify(entry), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
