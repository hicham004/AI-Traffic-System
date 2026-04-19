
import pygame
import sys
import random
import time

# Init
pygame.init()

# Constants
WIDTH, HEIGHT = 650, 620
SCREEN = pygame.display.set_mode((WIDTH + 190, HEIGHT))
pygame.display.set_caption("AI Traffic Prototype")

import os

BASE_DIR = os.path.dirname(__file__)
ASPHALT = pygame.image.load(os.path.join(BASE_DIR, "asphalt.jpg"))
INTERSECTION = pygame.image.load(os.path.join(BASE_DIR, "intersection.png"))
# Fixed bush positions


# Colors
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 215, 0)
CAR_COLOR = (230, 230, 230)
EMERGENCY_COLOR = (255, 0, 255)

# Dimensions
LANE_WIDTH = 80
CAR_WIDTH, CAR_HEIGHT = 16, 32
LIGHT_SIZE = 10
SPEED = 2

# Lanes
lanes = {
    "1_down": (0, HEIGHT // 2 + 10),
    "3_up": (WIDTH - CAR_HEIGHT, HEIGHT // 2 - CAR_WIDTH - 10),
    "2_left": (WIDTH // 2 - CAR_WIDTH - 10, 0),
    "4_right": (WIDTH // 2 + 10, HEIGHT - CAR_HEIGHT),
}

# Simulation State
class SimulationState:
    def __init__(self):
        self.active_lanes = []
        self.lane_timer = 0
        self.lane_duration = 5
        self.lane_queues = {k: [] for k in lanes}
        self.traffic_lights = {k: "RED" for k in lanes}

    def set_active_lanes(self, lanes_to_activate):
        for k in self.traffic_lights:
            self.traffic_lights[k] = "RED"
        for lane in lanes_to_activate:
            self.traffic_lights[lane] = "GREEN"
        self.active_lanes = lanes_to_activate
        self.lane_timer = time.time()
        save_light_state_to_file(self.traffic_lights)

state = SimulationState()


import json

LANE_MAP = {
    "1_down": "west",
    "2_left": "north",
    "3_up": "east",
    "4_right": "south"
}

def save_light_state_to_file(state_dict):
    mapped = {LANE_MAP[k]: v for k, v in state_dict.items()}
    json_path = os.path.join(os.path.dirname(__file__), "light_state.json")
    with open(json_path, "w") as f:
        json.dump(mapped, f)


# Patch for SimulationState

class Car:
    def __init__(self, lane, is_emergency=False, position=None):
        self.lane = lane
        self.is_emergency = is_emergency
        x, y = position if position else lanes[lane]
        if lane in ["1_down", "3_up"]:
            self.rect = pygame.Rect(x, y, CAR_HEIGHT, CAR_WIDTH)
        else:
            self.rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)

    def move(self):
        mid_x = WIDTH // 2
        mid_y = HEIGHT // 2
        passed = False

        if self.lane == "1_down":
            passed = self.rect.x > mid_x
            if state.traffic_lights[self.lane] == "GREEN" or passed:
                self.rect.x += SPEED
        elif self.lane == "3_up":
            passed = self.rect.x < mid_x
            if state.traffic_lights[self.lane] == "GREEN" or passed:
                self.rect.x -= SPEED
        elif self.lane == "2_left":
            passed = self.rect.y > mid_y
            if state.traffic_lights[self.lane] == "GREEN" or passed:
                self.rect.y += SPEED
        elif self.lane == "4_right":
            passed = self.rect.y < mid_y
            if state.traffic_lights[self.lane] == "GREEN" or passed:
                self.rect.y -= SPEED

    def draw(self):
        color = EMERGENCY_COLOR if self.is_emergency else CAR_COLOR
        pygame.draw.rect(SCREEN, color, self.rect)

        if self.is_emergency:
            # Draw light bar: red and blue pixels on top of the ambulance
            if self.lane in ["1_down", "3_up"]:  # horizontal
                pygame.draw.rect(SCREEN, (255, 0, 0), (self.rect.x + 2, self.rect.y + 2, 3, 3))
                pygame.draw.rect(SCREEN, (0, 0, 255), (self.rect.x + 10, self.rect.y + 2, 3, 3))
            else:  # vertical
                pygame.draw.rect(SCREEN, (255, 0, 0), (self.rect.x + 2, self.rect.y + 2, 3, 3))
                pygame.draw.rect(SCREEN, (0, 0, 255), (self.rect.x + 2, self.rect.y + 10, 3, 3))


def spawn_car(lane, is_emergency=False):
    offset_spacing = 50
    cars = state.lane_queues[lane]
    base_x, base_y = lanes[lane]
    if lane == "1_down":
        x = base_x + offset_spacing * len(cars)
        y = base_y
    elif lane == "3_up":
        x = base_x - offset_spacing * len(cars)
        y = base_y
    elif lane == "2_left":
        x = base_x
        y = base_y + offset_spacing * len(cars)
    elif lane == "4_right":
        x = base_x
        y = base_y - offset_spacing * len(cars)
    car = Car(lane, is_emergency, (x, y))
    state.lane_queues[lane].append(car)

# GUI
class Button:
    def __init__(self, rect, text, callback, bg_color=GRAY, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Button state
selected_lane = "1_down"
vehicle_type = "car"
vehicle_count = 1
simulation_running = True

# Button functions
def set_lane(lane): global selected_lane; selected_lane = lane
def toggle_vehicle_type(): global vehicle_type; vehicle_type = "ambulance" if vehicle_type == "car" else "car"
def increment_count(): global vehicle_count; vehicle_count = min(vehicle_count + 1, 5)
def decrement_count(): global vehicle_count; vehicle_count = max(vehicle_count - 1, 1)
def add_vehicles(): [spawn_car(selected_lane, vehicle_type == "ambulance") for _ in range(vehicle_count)]
def toggle_simulation(): global simulation_running; simulation_running = not simulation_running
def clear_all_cars(): [state.lane_queues.update({lane: []}) for lane in state.lane_queues]

# Buttons
buttons = [
    Button((WIDTH + 10, 20, 160, 30), "Lane 1 ", lambda: set_lane("1_down")),
    Button((WIDTH + 10, 60, 160, 30), "Lane 2 ", lambda: set_lane("2_left")),
    Button((WIDTH + 10, 100, 160, 30), "Lane 3 ", lambda: set_lane("3_up")),
    Button((WIDTH + 10, 140, 160, 30), "Lane 4 ", lambda: set_lane("4_right")),
    Button((WIDTH + 10, 180, 160, 30), "Toggle Type ", toggle_vehicle_type),
    Button((WIDTH + 10, 220, 40, 30), "-", decrement_count),
    Button((WIDTH + 130, 220, 40, 30), "+", increment_count),
    Button((WIDTH + 10, 260, 160, 30), "Add Vehicles", add_vehicles),
    Button((WIDTH + 10, 300, 160, 30), "Start/Stop", toggle_simulation),
    Button((WIDTH + 10, 340, 160, 30), "Clear All Cars", clear_all_cars),
]

# Draw environment
def draw_background():
    for x in range(0, WIDTH + 190, 64):
        for y in range(0, HEIGHT, 64):
            SCREEN.blit(ASPHALT, (x, y))

    

    mid = (WIDTH // 2 - 32, HEIGHT // 2 - 32)
    SCREEN.blit(INTERSECTION, mid)

    # Road boundaries
    pygame.draw.line(SCREEN, WHITE, (WIDTH // 2 - LANE_WIDTH, 0), (WIDTH // 2 - LANE_WIDTH, HEIGHT), 2)
    pygame.draw.line(SCREEN, WHITE, (WIDTH // 2 + LANE_WIDTH, 0), (WIDTH // 2 + LANE_WIDTH, HEIGHT), 2)
    pygame.draw.line(SCREEN, WHITE, (0, HEIGHT // 2 - LANE_WIDTH), (WIDTH, HEIGHT // 2 - LANE_WIDTH), 2)
    pygame.draw.line(SCREEN, WHITE, (0, HEIGHT // 2 + LANE_WIDTH), (WIDTH, HEIGHT // 2 + LANE_WIDTH), 2)

    mid_x, mid_y = WIDTH // 2, HEIGHT // 2
    gap = LANE_WIDTH // 2 + 10
    for y in range(0, mid_y - gap, 40):
        pygame.draw.line(SCREEN, WHITE, (mid_x, y), (mid_x, y + 20), 2)
    for y in range(mid_y + gap, HEIGHT, 40):
        pygame.draw.line(SCREEN, WHITE, (mid_x, y), (mid_x, y + 20), 2)
    for x in range(0, mid_x - gap, 40):
        pygame.draw.line(SCREEN, WHITE, (x, mid_y), (x + 20, mid_y), 2)
    for x in range(mid_x + gap, WIDTH, 40):
        pygame.draw.line(SCREEN, WHITE, (x, mid_y), (x + 20, mid_y), 2)

# Draw lights
def draw_lights():
    pos = {
    "1_down": (WIDTH  // 2 - LANE_WIDTH - 11 , HEIGHT // 2 + LANE_WIDTH - 12),   # 🔵 Point 1
    
    "2_left": (WIDTH // 2 - LANE_WIDTH + 12, HEIGHT // 2 - LANE_WIDTH - 12),   # 🔵 Point 2

    "3_up": (WIDTH // 2 + LANE_WIDTH + 12, HEIGHT // 2 - LANE_WIDTH + 12),     # 🔵 Point 3

    "4_right": (WIDTH // 2 + LANE_WIDTH - 12, HEIGHT // 2 + LANE_WIDTH + 12),  # 🔵 Point 4
}

    for lane, (x, y) in pos.items():
        pygame.draw.rect(SCREEN, (0, 255, 255), (x - 5, y - 5, 10, 10))  # Cyan debug square

    for lane, color in state.traffic_lights.items():
        c = GREEN if color == "GREEN" else RED if color == "RED" else YELLOW
        pygame.draw.circle(SCREEN, c, pos[lane], LIGHT_SIZE)

# Main loop
def run_simulation():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    while True:
        draw_background()
        draw_lights()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for btn in buttons:
                btn.handle_event(event)

        pygame.draw.rect(SCREEN, (30, 30, 30), (WIDTH, 0, 190, HEIGHT))
        for btn in buttons:
            btn.draw(SCREEN)

        SCREEN.blit(font.render(f"Lane: {selected_lane}", True, WHITE), (WIDTH + 10, 390))
        SCREEN.blit(font.render(f"Type: {vehicle_type}", True, WHITE), (WIDTH + 10, 420))
        SCREEN.blit(font.render(f"Count: {vehicle_count}", True, WHITE), (WIDTH + 10, 450))

        for lane, queue in state.lane_queues.items():
            for car in queue:
                if simulation_running:
                    car.move()
                car.draw()
        
        # Check override state
        override_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "override_state.json")
        if os.path.exists(override_path):
            with open(override_path, "r") as f:
                override_data = json.load(f)
            if override_data.get("manual_override") and override_data.get("forced_lane"):
                lane = override_data["forced_lane"]
                if lane == "north":
                    state.set_active_lanes(["2_left"])
                elif lane == "south":
                    state.set_active_lanes(["4_right"])
                elif lane == "east":
                    state.set_active_lanes(["3_up"])
                elif lane == "west":
                    state.set_active_lanes(["1_down"])



        if simulation_running and time.time() - state.lane_timer > state.lane_duration:

            emergency_lanes = [k for k, q in state.lane_queues.items() if any(c.is_emergency for c in q)]
            if emergency_lanes:
                if "1_down" in emergency_lanes or "3_up" in emergency_lanes:
                    state.set_active_lanes(["1_down", "3_up"])
                elif "2_left" in emergency_lanes or "4_right" in emergency_lanes:
                    state.set_active_lanes(["2_left", "4_right"])
            else:
                horiz = len(state.lane_queues["1_down"]) + len(state.lane_queues["3_up"])
                vert = len(state.lane_queues["2_left"]) + len(state.lane_queues["4_right"])
                if horiz >= vert:
                    state.set_active_lanes(["1_down", "3_up"])
                else:
                    state.set_active_lanes(["2_left", "4_right"])

        for lane in state.lane_queues:
            state.lane_queues[lane] = [car for car in state.lane_queues[lane] if 0 <= car.rect.x <= WIDTH and 0 <= car.rect.y <= HEIGHT]
    # Display emergency status if any emergency vehicle is present
        # Display emergency status if any emergency vehicle is present
        if any(c.is_emergency for q in state.lane_queues.values() for c in q):
            alert_font = pygame.font.SysFont(None, 28, bold=True)
            alert_text = alert_font.render("Emergency Vehicle Prioritization Active!", True, WHITE)
            SCREEN.blit(alert_text, (WIDTH // 2 - alert_text.get_width() // 2, 10))

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    run_simulation()
