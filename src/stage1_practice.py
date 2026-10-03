# STAGE 1: Python Fundamentals for Computer Vision
# This script simulates how variables, tuples, lists, and loops 
# are used in our Air Drawing project!

# 1. Variables and Data Types
project_name = "Air Drawing"          # String (text)
brush_size = 5                        # Integer (whole number)
confidence_threshold = 0.75           # Float (decimal number)
is_drawing = True                     # Boolean (True / False)

# 2. Tuples: Perfect for Coordinates (x, y) and Colors (Blue, Green, Red)
fingertip_coordinate = (320, 240)     # (x, y) - immutable pair
brush_color = (255, 0, 0)             # (Blue, Green, Red) tuple

# 3. Lists: Perfect for storing drawing strokes over time
drawn_points = []                     # An empty list to hold coordinates

# 4. Functions: Reusable blocks of logic
def add_point_to_canvas(point, status):
    """Adds a coordinate to our drawing list if drawing mode is active."""
    if status is True:
        drawn_points.append(point)
        return f"Point {point} added to canvas!"
    else:
        return "Drawing paused. No point added."

# 5. Loops and Conditionals: Simulating 5 frames from a webcam
simulated_finger_positions = [
    (100, 150),
    (110, 155),
    (125, 160),
    (140, 170),
    (160, 185)
]

print("--- Simulating Camera Frame Loop ---")
for frame_number, pos in enumerate(simulated_finger_positions, start=1):
    result = add_point_to_canvas(pos, is_drawing)
    print(f"Frame {frame_number}: Finger at {pos} -> {result}")

print("\n--- Summary of Drawn Stroke ---")
print(f"Total points recorded: {len(drawn_points)}")
print(f"Points list: {drawn_points}")
