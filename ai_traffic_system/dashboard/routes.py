import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify, request, send_file
from app import state
from app.db.db_manager import (
    get_active_incidents,
    get_on_call_officers,
    log_incident,
    log_system_event,
    get_recent_logs
)

import csv
from io import BytesIO
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    return jsonify({
        "lane_counts": state.lane_counts,
        "override": state.override_state
    })

@app.route("/api/override", methods=["POST"])
def set_override():
    data = request.json
    enabled = data.get("enabled", False)
    lane = data.get("lane")

    override_state = {
        "manual_override": enabled,
        "forced_lane": lane if enabled else None
    }

    override_path = os.path.join(os.path.dirname(__file__), "override_state.json")
    with open(override_path, "w") as f:
        json.dump(override_state, f)

    log_system_event("override", f"{'enabled' if enabled else 'disabled'} → {lane if enabled else 'none'}")

    return jsonify({
        "success": True,
        "new_state": override_state
    })


@app.route("/api/incidents")
def incidents():
    try:
        data = get_active_incidents()
        return jsonify([{
            "id": row[0],
            "intersection_id": row[1],
            "timestamp": row[2],
            "type": row[3],
            "lane": row[4],
            "folder": row[5]
        } for row in data])
    except Exception as e:
        return jsonify([])  # Return empty list if DB is broken


@app.route("/api/officers")
def officers():
    try:
        data = get_on_call_officers()
        return jsonify([{
            "id": row[0],
            "name": row[1],
            "zone": row[2],
            "phone": row[3],
            "on_call": bool(row[4])
        } for row in data])
    except Exception as e:
        return jsonify([])  # Return empty list if DB is broken

@app.route("/api/recommendation")
def recommendation():
    lane_counts = state.lane_counts
    if all(v == 0 for v in lane_counts.values()):
        return jsonify({"lane": None, "count": 0})
    best_lane = max(lane_counts, key=lane_counts.get)
    return jsonify({"lane": best_lane, "count": lane_counts[best_lane]})

@app.route("/api/simulate_violation", methods=["POST"])
def simulate_violation():
    lanes = ["north", "south", "east", "west"]
    random_lane = random.choice(lanes)
    folder = f"demo_incident_{random.randint(1000, 9999)}"
    log_incident(intersection_id=1, type_="simulated_violation", lane=random_lane, image_folder=folder)
    log_system_event("demo", f"Simulated violation on lane {random_lane}")
    return jsonify({"success": True, "lane": random_lane})

@app.route("/api/lights")
def get_lights():
    import json
    import os

    json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "simulation", "light_state.json")
    )
    override_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "override_state.json")
    )

    try:
        with open(json_path, "r") as f:
            light_data = json.load(f)

        # Apply override if enabled
        if os.path.exists(override_path):
            with open(override_path, "r") as f:
                override = json.load(f)
            if override.get("manual_override") and override.get("forced_lane"):
                forced = override["forced_lane"]
                light_data = {k: "RED" for k in light_data}  # reset all
                light_data[forced] = "GREEN"  # apply override

        return jsonify(light_data)

    except Exception as e:
        return jsonify({
            "north": "RED", "south": "RED", "east": "RED", "west": "RED",
            "error": str(e)
        })





@app.route("/api/export_report")
def export_report():
    rows = get_active_incidents()
    text_data = "ID,Intersection,Timestamp,Type,Lane,Folder,Status\n"
    for row in rows:
        text_data += ",".join(map(str, row)) + "\n"

    csv_buffer = BytesIO()
    csv_buffer.write(text_data.encode("utf-8"))
    csv_buffer.seek(0)

    log_system_event("export", "CSV incident report generated")

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        download_name="incident_report.csv",
        as_attachment=True
    )

@app.route("/api/logs")
def fetch_logs():
    try:
        logs = get_recent_logs()
        return jsonify([
            {"timestamp": ts, "event_type": etype, "description": desc}
            for ts, etype, desc in logs
        ])
    except Exception as e:
        return jsonify([])  # Return empty list if DB is broken

