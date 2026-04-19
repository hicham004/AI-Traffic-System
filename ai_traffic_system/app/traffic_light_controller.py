
# app/traffic_light_controller.py

import time
from app import state

class TrafficLightController:
    def __init__(self):
        self.current_lane = None
        self.current_state = "RED"
        self.last_switch_time = time.time()
        self.min_green = 10
        self.max_green = 45
        self.yellow_duration = 2
        self.yellow_start_time = None
        self.is_yellow = False

    def update_light(self, lane_counts):
        now = time.time()
        time_since_yolo = now - state.system_status["last_yolo_heartbeat"]

        # Determine system mode
        if time_since_yolo > 5:
            state.system_status["mode"] = "FAILSAFE"
        else:
            state.system_status["mode"] = "AI"

        # Failsafe mode: default cycle
        if state.system_status["mode"] == "FAILSAFE":
            return self._default_cycle(now)

        # If in yellow phase, hold it for yellow_duration
        if self.is_yellow:
            if now - self.yellow_start_time < self.yellow_duration:
                self.current_state = "YELLOW"
                return self.current_lane, "YELLOW"
            else:
                self.is_yellow = False
                self.current_state = "RED"
                return None, "RED"

        # Emergency override
        if state.override_state["manual_override"]:
            forced_lane = state.override_state["forced_lane"]
            if self.current_lane != forced_lane:
                if self.current_lane:
                    self._start_yellow()
                    return self.current_lane, "YELLOW"
                else:
                    self._switch_to(forced_lane)
                    return forced_lane, "GREEN"
            return forced_lane, "GREEN"

        # Normal AI logic
        if self.current_lane:
            duration = now - self.last_switch_time
            if duration < self.min_green:
                return self.current_lane, "GREEN"
            if duration >= self.max_green:
                self._start_yellow()
                return self.current_lane, "YELLOW"

            top_lane = max(lane_counts, key=lane_counts.get)
            if lane_counts[top_lane] > lane_counts[self.current_lane] + 3:
                self._start_yellow()
                return self.current_lane, "YELLOW"
            return self.current_lane, "GREEN"

        next_lane = self._select_best_lane(lane_counts)
        if next_lane:
            self._switch_to(next_lane)
            return next_lane, "GREEN"
        return None, "RED"

    def _start_yellow(self):
        self.is_yellow = True
        self.yellow_start_time = time.time()
        self.current_state = "YELLOW"

    def _switch_to(self, lane):
        self.current_lane = lane
        self.last_switch_time = time.time()
        self.current_state = "GREEN"

    def _select_best_lane(self, lane_counts):
        if all(v == 0 for v in lane_counts.values()):
            return None
        return max(lane_counts, key=lane_counts.get)

    def _default_cycle(self, now):
        lanes = ["north", "east", "south", "west"]
        cycle_time = 15
        index = int((now // cycle_time) % len(lanes))
        return lanes[index], "GREEN"
