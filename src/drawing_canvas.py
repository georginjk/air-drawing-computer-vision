# STAGE 11: Modular Architecture - Canvas Manager
# Handles the persistent digital canvas, stroke drawing, erasing, 
# 2D pixel masking, and exporting to Windows Pictures.

import cv2
import numpy as np
import os
from datetime import datetime
from config import PICTURES_DIR, ASSETS_DIR

class CanvasManager:
    def __init__(self, frame_height, frame_width):
        self.height = frame_height
        self.width = frame_width
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def draw_stroke(self, prev_point, curr_point, color, thickness):
        """Draws a continuous line segment onto the persistent canvas."""
        cv2.line(self.canvas, prev_point, curr_point, color, thickness)

    def erase_stroke(self, prev_point, curr_point, thickness):
        """Erases pixels by stamping black (0, 0, 0) along line and at point."""
        cv2.circle(self.canvas, curr_point, thickness // 2, (0, 0, 0), cv2.FILLED)
        if prev_point is not None:
            cv2.line(self.canvas, prev_point, curr_point, (0, 0, 0), thickness)

    def clear(self):
        """Wipes the digital canvas completely."""
        self.canvas.fill(0)

    def merge_with_frame(self, frame):
        """
        Overlays the persistent canvas onto the live camera frame
        using an exact 2D boolean pixel mask.
        """
        pixel_mask = np.any(self.canvas > 0, axis=-1)
        display_frame = frame.copy()
        display_frame[pixel_mask] = self.canvas[pixel_mask]
        return display_frame

    def save_drawing(self):
        """
        Exports the artwork on a pure white digital paper (255, 255, 255)
        to Windows Pictures/AirDrawing (and a backup to assets/).
        Returns the filename.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"air_drawing_{timestamp}.png"

        pictures_path = os.path.join(PICTURES_DIR, filename)
        assets_path = os.path.join(ASSETS_DIR, filename)

        # White paper background
        white_paper = np.full((self.height, self.width, 3), 255, dtype=np.uint8)
        pixel_mask = np.any(self.canvas > 0, axis=-1)
        white_paper[pixel_mask] = self.canvas[pixel_mask]

        # Save to both locations
        cv2.imwrite(pictures_path, white_paper)
        cv2.imwrite(assets_path, white_paper)

        print(f"[SAVE] Exported artwork to {pictures_path}")
        return filename
