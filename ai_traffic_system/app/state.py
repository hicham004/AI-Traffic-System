
# app/state.py

# Live lane counts (shared between modules)
lane_counts = {
    "north": 0,
    "south": 0,
    "east": 0,
    "west": 0
}

# Manual override state
override_state = {
    "manual_override": False,
    "forced_lane": None
}

# System status (AI health, fallback triggers)
system_status = {
    "mode": "AI",  # or "FAILSAFE"
    "last_yolo_heartbeat": 0.0
}
