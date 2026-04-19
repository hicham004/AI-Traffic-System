# app/intersection_config.py

intersection_config = {
    "id": "gemmayzeh_1",
    "name": "Gemmayzeh Main Intersection",
    "location": {
        "lat": 33.894694,
        "lng": 35.512111
    },
    "camera_zones": {
        "north": "cam01",  # Facing north up Gouraud
        "south": "cam02",  # Facing south toward Mar Mikhael
        "east": "cam03",   # Narrow alley near Electricité du Liban
        "west": "cam04"    # Side street facing toward Beirut port
    },
    "map_rotation_deg": 12,  # Estimate: angle between map "up" and true north
    "notes": "Real-world testbed. Cameras suspected active. Ideal for 4-direction layout."
}
