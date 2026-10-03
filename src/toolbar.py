# STAGE 11: Modular Architecture - Toolbar Component
# Handles layout, button hit-testing, and UI rendering.

import cv2
from config import COLORS, TOOLBAR_HEIGHT, BRUSH_SIZES

class Toolbar:
    def __init__(self, frame_width):
        self.frame_width = frame_width
        self.height = TOOLBAR_HEIGHT
        
        # 10 Interactive Buttons
        self.buttons = [
            {"name": "RED",    "color": COLORS["RED"],     "type": "color"},
            {"name": "GREEN",  "color": COLORS["GREEN"],   "type": "color"},
            {"name": "BLUE",   "color": COLORS["BLUE"],    "type": "color"},
            {"name": "YELLOW", "color": COLORS["YELLOW"],  "type": "color"},
            {"name": "PURPLE", "color": COLORS["PURPLE"],  "type": "color"},
            {"name": "ORANGE", "color": COLORS["ORANGE"],  "type": "color"},
            {"name": "SIZE",   "color": (80, 80, 80),      "type": "size"},
            {"name": "ERASER", "color": COLORS["BLACK"],   "type": "eraser"},
            {"name": "SAVE",   "color": (140, 70, 0),      "type": "save"},
            {"name": "CLEAR",  "color": (45, 45, 45),      "type": "clear"}
        ]
        
        btn_width = self.frame_width // len(self.buttons)
        for i, btn in enumerate(self.buttons):
            btn["x1"] = i * btn_width + 3
            btn["x2"] = (i + 1) * btn_width - 3

    def check_interaction(self, x, y):
        """Checks if a point (x, y) clicked any button. Returns button dict or None."""
        if y < self.height:
            for btn in self.buttons:
                if btn["x1"] <= x <= btn["x2"]:
                    return btn
        return None

    def draw(self, display_frame, current_tool_name, current_brush_thickness):
        """Renders the top toolbar onto the display frame."""
        cv2.rectangle(display_frame, (0, 0), (self.frame_width, self.height), (20, 20, 20), -1)
        cv2.line(display_frame, (0, self.height), (self.frame_width, self.height), (80, 80, 80), 2)

        for btn in self.buttons:
            x1, x2 = btn["x1"], btn["x2"]
            is_selected = (btn["name"] == current_tool_name)

            if btn["type"] == "color":
                cv2.rectangle(display_frame, (x1, 10), (x2, 65), btn["color"], -1)
                text_color = (0, 0, 0) if btn["name"] in ["YELLOW", "GREEN", "ORANGE"] else (255, 255, 255)
                cv2.putText(display_frame, btn["name"][:3], (x1 + 6, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 2)

            elif btn["type"] == "size":
                cv2.rectangle(display_frame, (x1, 10), (x2, 65), (55, 55, 55), -1)
                cv2.putText(display_frame, f"{current_brush_thickness}px", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

            elif btn["type"] == "eraser":
                bg = (210, 210, 210) if is_selected else (60, 60, 60)
                txt_col = (0, 0, 0) if is_selected else (240, 240, 240)
                cv2.rectangle(display_frame, (x1, 10), (x2, 65), bg, -1)
                cv2.putText(display_frame, "ERAS", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, txt_col, 2)

            elif btn["type"] == "save":
                cv2.rectangle(display_frame, (x1, 10), (x2, 65), btn["color"], -1)
                cv2.putText(display_frame, "SAVE", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

            elif btn["type"] == "clear":
                cv2.rectangle(display_frame, (x1, 10), (x2, 65), btn["color"], -1)
                cv2.putText(display_frame, "CLR", (x1 + 8, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 140, 255), 2)

            if is_selected:
                cv2.rectangle(display_frame, (x1 - 2, 7), (x2 + 2, 68), (255, 255, 255), 3)
