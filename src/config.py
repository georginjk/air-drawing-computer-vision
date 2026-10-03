# STAGE 11: Modular Architecture - Configuration Settings
# This file centralizes all constants, colors, thresholds, and paths.

import os
from pathlib import Path

# --- DIRECTORY PATHS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
PICTURES_DIR = os.path.join(Path.home(), "Pictures", "AirDrawing")

# Ensure required folders exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(PICTURES_DIR, exist_ok=True)

# --- CAMERA & DISPLAY ---
DEFAULT_CAMERA_INDEX = 0
WINDOW_TITLE = "Air Drawing Studio - Computer Vision"
TOOLBAR_HEIGHT = 75

# --- ALGORITHM TUNING ---
SMOOTHING_FACTOR = 0.65       # Coordinate smoothing (0.0 to 1.0)
STABILITY_THRESHOLD = 3      # Debounce frames for continuous strokes
JUMP_THRESHOLD = 180         # Maximum allowed pixel jump per frame

# --- BRUSH & ERASER ---
BRUSH_SIZES = [4, 8, 14, 22]
DEFAULT_SIZE_INDEX = 1       # 8px default
ERASER_THICKNESS = 45

# --- COLOR DEFINITIONS (BGR Format) ---
COLORS = {
    "RED": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (255, 0, 0),
    "YELLOW": (0, 255, 255),
    "PURPLE": (255, 0, 200),
    "ORANGE": (0, 140, 255),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (120, 120, 120),
    "DARK_GRAY": (30, 30, 30),
    "CYAN": (255, 200, 0)
}
