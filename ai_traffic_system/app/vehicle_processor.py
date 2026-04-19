# app/vehicle_processor.py

class VehicleProcessor:
    def __init__(self, width, height):
        self.frame_width = width
        self.frame_height = height

    def count_vehicles_per_lane(self, detections):
        """
        Classify each detection into a directional lane
        based on its center position in the frame.
        """
        counts = {"north": 0, "south": 0, "east": 0, "west": 0}
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if cx < self.frame_width // 2 and cy < self.frame_height // 2:
                counts["north"] += 1
            elif cx > self.frame_width // 2 and cy < self.frame_height // 2:
                counts["east"] += 1
            elif cx < self.frame_width // 2 and cy > self.frame_height // 2:
                counts["west"] += 1
            else:
                counts["south"] += 1
        return counts

    def count_vehicles_in_zone(self, detections, zone):
        """
        Get count of vehicles for a single zone, based on full-frame quadrant logic.
        """
        lane_counts = self.count_vehicles_per_lane(detections)
        return lane_counts.get(zone, 0)
