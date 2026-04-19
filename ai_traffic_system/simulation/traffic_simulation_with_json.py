import pygame
import sys
import random
import time
import json

pygame.init()

# Screen setup
WIDTH, HEIGHT = 650, 620
SCREEN = pygame.display.set_mode((WIDTH + 190, HEIGHT))  # Add GUI area
pygame.display.set_caption("AI Traffic Prototype")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 215, 0)
CAR_COLOR = (230, 230, 230)
EMERGENCY_COLOR = (255, 0, 255)

LANE_WIDTH = 80
CAR_WIDTH, CAR_HEIGHT = 20, 40
LIGHT_SIZE = 10
SPEED = 2

# Lane positions
lanes = {
    "1_down": (0, HEIGHT // 2 + 10),
    "3_up": (WIDTH - CAR_HEIGHT, HEIGHT // 2 - CAR_WIDTH - 10),
    "2_left": (WIDTH // 2 - CAR_WIDTH - 10, 0),
    "4_right": (WIDTH // 2 + 10, HEIGHT - CAR_HEIGHT),
}

LANE_MAP = {
    "1_down": "west",
    "2_left": "north",
    "3_up": "east",
    "4_right": "south"
}

def save_light_state_to_file(state_dict):
    mapped = {LANE_MAP[k]: v for k, v in state_dict.items()}
    with open("light_state.json", "w") as f:
        json.dump(mapped, f)


class SimulationState:
    def __init__(self):
        self.active_lane = None
        self.lane_timer = 0
        self.lane_duration = 5
        self.override_lane = None
        self.lane_queues = {k: [] for k in lanes}
        self.traffic_lights = {k: "RED" for k in lanes}

    def set_active_lane(self, lane):
        for k in self.traffic_lights:
            self.traffic_lights[k] = "RED"
        if lane:
            self.traffic_lights[lane] = "GREEN"
            self.active_lane = lane
            self.lane_timer = time.time()
        save_light_state_to_file(self.traffic_lights)

state = SimulationState()

class Car:
    def __init__(self, lane, is_emergency=False, position=None):
        self.lane = lane
        self.is_emergency = is_emergency
        x, y = position if position else lanes[lane]

        if lane in ["1_down", "3_up"]:
            self.rect = pygame.Rect(x, y, CAR_HEIGHT, CAR_WIDTH)  # Horizontal
        else:
            self.rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)  # Vertical

    def move(self):
        passed_intersection = False

        if self.lane == "1_down":
            passed_intersection = self.rect.x > WIDTH // 2 - LANE_WIDTH // 2
            if state.traffic_lights[self.lane] == "GREEN" or self.is_emergency or passed_intersection:
                self.rect.x += SPEED
        elif self.lane == "3_up":
            passed_intersection = self.rect.x < WIDTH // 2 + LANE_WIDTH // 2
            if state.traffic_lights[self.lane] == "GREEN" or passed_intersection:
                self.rect.x -= SPEED
        elif self.lane == "2_left":
            passed_intersection = self.rect.y > HEIGHT // 2 - LANE_WIDTH // 2
            if state.traffic_lights[self.lane] == "GREEN" or passed_intersection:
                self.rect.y += SPEED
        elif self.lane == "4_right":
            passed_intersection = self.rect.y < HEIGHT // 2 + LANE_WIDTH // 2
            if state.traffic_lights[self.lane] == "GREEN" or passed_intersection:
                self.rect.y -= SPEED

    def draw(self):
        color = EMERGENCY_COLOR if self.is_emergency else CAR_COLOR
        pygame.draw.rect(SCREEN, color, self.rect)

def draw_background():
    SCREEN.fill(GRAY)
    pygame.draw.line(SCREEN, WHITE, (WIDTH // 2 - LANE_WIDTH, 0), (WIDTH // 2 - LANE_WIDTH, HEIGHT), 2)
    pygame.draw.line(SCREEN, WHITE, (WIDTH // 2 + LANE_WIDTH, 0), (WIDTH // 2 + LANE_WIDTH, HEIGHT), 2)
    pygame.draw.line(SCREEN, WHITE, (0, HEIGHT // 2 - LANE_WIDTH), (WIDTH, HEIGHT // 2 - LANE_WIDTH), 2)
    pygame.draw.line(SCREEN, WHITE, (0, HEIGHT // 2 + LANE_WIDTH), (WIDTH, HEIGHT // 2 + LANE_WIDTH), 2)

    mid_x = WIDTH // 2
    mid_y = HEIGHT // 2
    gap = LANE_WIDTH // 2 + 10

    for y in range(0, mid_y - gap, 40):
        pygame.draw.line(SCREEN, WHITE, (mid_x, y), (mid_x, y + 20), 2)
    for y in range(mid_y + gap, HEIGHT, 40):
        pygame.draw.line(SCREEN, WHITE, (mid_x, y), (mid_x, y + 20), 2)
    for x in range(0, mid_x - gap, 40):
        pygame.draw.line(SCREEN, WHITE, (x, mid_y), (x + 20, mid_y), 2)
    for x in range(mid_x + gap, WIDTH, 40):
        pygame.draw.line(SCREEN, WHITE, (x, mid_y), (x + 20, mid_y), 2)

def draw_lights():
    pos = {
        "1_down": (WIDTH // 2 - LANE_WIDTH - 30, HEIGHT // 2 + LANE_WIDTH // 2 + 10),
        "3_up":   (WIDTH // 2 + LANE_WIDTH + 30, HEIGHT // 2 - LANE_WIDTH // 2 - 10),
        "2_left": (WIDTH // 2 - LANE_WIDTH // 2 + 25, HEIGHT // 2 - LANE_WIDTH - 30),
        "4_right":(WIDTH // 2 + LANE_WIDTH // 2 - 25, HEIGHT // 2 + LANE_WIDTH + 30),
    }

    for lane, color in state.traffic_lights.items():
        c = GREEN if color == "GREEN" else RED if color == "RED" else YELLOW
        pygame.draw.circle(SCREEN, c, pos[lane], LIGHT_SIZE)

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

def clear_all_cars():
    for lane in state.lane_queues:
        state.lane_queues[lane] = []

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

selected_lane = "1_down"
vehicle_type = "car"
vehicle_count = 1
simulation_running = True

def set_lane(lane): 
    global selected_lane 
    selected_lane = lane

def toggle_vehicle_type(): 
    global vehicle_type 
    vehicle_type = "ambulance" if vehicle_type == "car" else "car"

def increment_count(): 
    global vehicle_count 
    vehicle_count = min(vehicle_count + 1, 5)

def decrement_count(): 
    global vehicle_count 
    vehicle_count = max(vehicle_count - 1, 1)

def add_vehicles(): 
    for _ in range(vehicle_count):
        spawn_car(selected_lane, vehicle_type == "ambulance")

def toggle_simulation(): 
    global simulation_running 
    simulation_running = not simulation_running

buttons = [
    Button((WIDTH + 10, 20, 160, 30), "Lane 1 (←)", lambda: set_lane("1_down")),
    Button((WIDTH + 10, 60, 160, 30), "Lane 2 (↑)", lambda: set_lane("2_left")),
    Button((WIDTH + 10, 100, 160, 30), "Lane 3 (→)", lambda: set_lane("3_up")),
    Button((WIDTH + 10, 140, 160, 30), "Lane 4 (↓)", lambda: set_lane("4_right")),
    Button((WIDTH + 10, 180, 160, 30), "Toggle Type 🚗/🚑", toggle_vehicle_type),
    Button((WIDTH + 10, 220, 40, 30), "-", decrement_count),
    Button((WIDTH + 130, 220, 40, 30), "+", increment_count),
    Button((WIDTH + 10, 260, 160, 30), "Add Vehicles", add_vehicles),
    Button((WIDTH + 10, 300, 160, 30), "Start/Stop", toggle_simulation),
    Button((WIDTH + 10, 340, 160, 30), "Clear All Cars", clear_all_cars),
]

def run_simulation():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    while True:
        draw_background()
        draw_lights()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for btn in buttons:
                btn.handle_event(event)

        pygame.draw.rect(SCREEN, (30, 30, 30), (WIDTH, 0, 190, HEIGHT))
        for btn in buttons:
            btn.draw(SCREEN)

        label_lane = font.render(f"Lane: {selected_lane}", True, WHITE)
        label_type = font.render(f"Type: {vehicle_type}", True, WHITE)
        label_count = font.render(f"Count: {vehicle_count}", True, WHITE)
        SCREEN.blit(label_lane, (WIDTH + 10, 380))
        SCREEN.blit(label_type, (WIDTH + 10, 410))
        SCREEN.blit(label_count, (WIDTH + 10, 440))

        for lane, queue in state.lane_queues.items():
            for car in queue:
                if simulation_running:
                    car.move()
                car.draw()

        if simulation_running and time.time() - state.lane_timer > state.lane_duration:
            emergency_lane = next((k for k, q in state.lane_queues.items() if any(c.is_emergency for c in q)), None)
            if emergency_lane:
                state.set_active_lane(emergency_lane)
            else:
                most_cars = max(state.lane_queues.items(), key=lambda item: len(item[1]))[0]
                state.set_active_lane(most_cars)

        for lane in state.lane_queues:
            state.lane_queues[lane] = [car for car in state.lane_queues[lane] if 0 <= car.rect.x <= WIDTH and 0 <= car.rect.y <= HEIGHT]

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    run_simulation()
