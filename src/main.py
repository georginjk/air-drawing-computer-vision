# STAGE 11: Modular Architecture - Main Application Entry Point
# Connects HandDetector, Toolbar, CanvasManager, and Camera into a professional, cohesive pipeline.

import cv2
import math
import numpy as np

from config import (
    DEFAULT_CAMERA_INDEX, WINDOW_TITLE, TOOLBAR_HEIGHT,
    SMOOTHING_FACTOR, STABILITY_THRESHOLD, JUMP_THRESHOLD,
    BRUSH_SIZES, DEFAULT_SIZE_INDEX, ERASER_THICKNESS, COLORS
)
from hand_tracking import HandDetector
from toolbar import Toolbar
from drawing_canvas import CanvasManager

def main():
    # 1. Initialize Camera
    camera = cv2.VideoCapture(DEFAULT_CAMERA_INDEX)
    if not camera.isOpened():
        print(f"Error: Could not open camera {DEFAULT_CAMERA_INDEX}.")
        return

    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 2. Initialize Architecture Components
    detector = HandDetector(mode=False, max_hands=1, detection_con=0.6, track_con=0.5)
    toolbar = Toolbar(frame_width)
    canvas_manager = CanvasManager(frame_height, frame_width)

    # 3. Application State Variables
    size_index = DEFAULT_SIZE_INDEX
    brush_thickness = BRUSH_SIZES[size_index]
    current_color = COLORS["YELLOW"]
    current_tool_name = "YELLOW"

    # Smoothing & Debounce State
    prev_x, prev_y = None, None
    smooth_x, smooth_y = None, None
    frames_since_draw = STABILITY_THRESHOLD
    btn_cooldown = 0

    # Notification Banner
    notification_text = "Air Drawing Studio Ready!"
    notification_timer = 90

    print("=" * 65)
    print("  AIR DRAWING STUDIO - PRODUCTION APPLICATION")
    print("=" * 65)
    print("Controls:")
    print("  - ☝️  1 Finger on Canvas: Draw or Erase")
    print("  - ✌️  2 Fingers on Canvas: Hover / Move without drawing")
    print("  - Touch any top Toolbar button to select tools or actions")
    print("  - Press 's': Save | 'c': Clear | 'q': Quit")
    print("=" * 65)

    while True:
        success, frame = camera.read()
        if not success:
            print("Failed to read frame from camera.")
            break

        # Mirror flip
        frame = cv2.flip(frame, 1)

        # Detect Hand
        lmList = detector.find_hands(frame, draw=True)

        mode = "STANDBY"
        mode_color = COLORS["GRAY"]

        if btn_cooldown > 0:
            btn_cooldown -= 1

        if lmList:
            index_open, middle_open = detector.check_finger_states(lmList)
            raw_x, raw_y = detector.get_pixel_coords(lmList[8], frame_width, frame_height)

            # Coordinate Smoothing (EMA)
            if smooth_x is None or smooth_y is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = int(SMOOTHING_FACTOR * raw_x + (1 - SMOOTHING_FACTOR) * smooth_x)
                smooth_y = int(SMOOTHING_FACTOR * raw_y + (1 - SMOOTHING_FACTOR) * smooth_y)

            # --- CASE 1: TOOLBAR INTERACTION ---
            if smooth_y < toolbar.height:
                mode = "CHOOSING"
                mode_color = COLORS["CYAN"]
                prev_x, prev_y = None, None

                # Selection Reticle
                cv2.circle(frame, (smooth_x, smooth_y), 12, COLORS["WHITE"], 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, COLORS["CYAN"], cv2.FILLED)

                btn = toolbar.check_interaction(smooth_x, smooth_y)
                if btn and btn_cooldown == 0:
                    if btn["type"] == "color":
                        current_color = btn["color"]
                        current_tool_name = btn["name"]
                        notification_text = f"Color: {current_tool_name}"
                        notification_timer = 45

                    elif btn["type"] == "eraser":
                        current_color = COLORS["BLACK"]
                        current_tool_name = "ERASER"
                        notification_text = "Tool: ERASER"
                        notification_timer = 45

                    elif btn["type"] == "size":
                        size_index = (size_index + 1) % len(BRUSH_SIZES)
                        brush_thickness = BRUSH_SIZES[size_index]
                        notification_text = f"Brush Size: {brush_thickness}px"
                        notification_timer = 45
                        btn_cooldown = 15

                    elif btn["type"] == "save":
                        filename = canvas_manager.save_drawing()
                        notification_text = f"Saved: {filename}"
                        notification_timer = 90
                        btn_cooldown = 20

                    elif btn["type"] == "clear":
                        canvas_manager.clear()
                        current_tool_name = "YELLOW"
                        current_color = COLORS["YELLOW"]
                        notification_text = "Canvas Cleared!"
                        notification_timer = 45
                        btn_cooldown = 15

            # --- CASE 2: DRAWING OR ERASING (1 Finger on Canvas) ---
            elif index_open and not middle_open:
                mode = "ERASING" if current_tool_name == "ERASER" else "DRAWING"
                mode_color = (0, 200, 255) if current_tool_name == "ERASER" else COLORS["GREEN"]
                frames_since_draw = 0

                active_thickness = ERASER_THICKNESS if current_tool_name == "ERASER" else brush_thickness

                # Cursor display
                if current_tool_name == "ERASER":
                    cv2.circle(frame, (smooth_x, smooth_y), active_thickness // 2, COLORS["WHITE"], 2)
                    cv2.putText(frame, "E", (smooth_x - 5, smooth_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLORS["WHITE"], 1)
                else:
                    cv2.circle(frame, (smooth_x, smooth_y), active_thickness // 2 + 2, current_color, cv2.FILLED)
                    cv2.circle(frame, (smooth_x, smooth_y), active_thickness // 2 + 4, COLORS["WHITE"], 1)

                if prev_x is None or prev_y is None:
                    prev_x, prev_y = smooth_x, smooth_y
                    if current_tool_name == "ERASER":
                        canvas_manager.erase_stroke(None, (smooth_x, smooth_y), active_thickness)
                else:
                    dist = math.hypot(smooth_x - prev_x, smooth_y - prev_y)
                    if dist < JUMP_THRESHOLD:
                        if current_tool_name == "ERASER":
                            canvas_manager.erase_stroke((prev_x, prev_y), (smooth_x, smooth_y), active_thickness)
                        else:
                            canvas_manager.draw_stroke((prev_x, prev_y), (smooth_x, smooth_y), current_color, active_thickness)
                    prev_x, prev_y = smooth_x, smooth_y

            # --- CASE 3: HOVER / PEN UP (2 Fingers on Canvas) ---
            elif index_open and middle_open:
                mode = "HOVER (PEN UP)"
                mode_color = COLORS["ORANGE"]
                prev_x, prev_y = None, None
                frames_since_draw = STABILITY_THRESHOLD

                cv2.circle(frame, (smooth_x, smooth_y), 16, COLORS["WHITE"], 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, COLORS["WHITE"], cv2.FILLED)

            # --- CASE 4: DEBOUNCE / STANDBY ---
            else:
                frames_since_draw += 1
                if frames_since_draw < STABILITY_THRESHOLD and prev_x is not None:
                    active_thickness = ERASER_THICKNESS if current_tool_name == "ERASER" else brush_thickness
                    if current_tool_name == "ERASER":
                        canvas_manager.erase_stroke((prev_x, prev_y), (smooth_x, smooth_y), active_thickness)
                    else:
                        canvas_manager.draw_stroke((prev_x, prev_y), (smooth_x, smooth_y), current_color, active_thickness)
                    prev_x, prev_y = smooth_x, smooth_y
                else:
                    mode = "STANDBY"
                    mode_color = COLORS["GRAY"]
                    prev_x, prev_y = None, None

        else:
            frames_since_draw = STABILITY_THRESHOLD
            prev_x, prev_y = None, None
            smooth_x, smooth_y = None, None

        # 4. Merge Persistent Canvas onto Frame
        display_frame = canvas_manager.merge_with_frame(frame)

        # 5. Render Toolbar & Status Bar
        toolbar.draw(display_frame, current_tool_name, brush_thickness)

        status_text = f"MODE: {mode} | TOOL: {current_tool_name} ({brush_thickness}px)"
        cv2.putText(display_frame, status_text, (15, frame_height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.52, mode_color, 2)

        # Notification Banner
        if notification_timer > 0:
            notification_timer -= 1
            box_w = 340
            cv2.rectangle(display_frame, (frame_width // 2 - box_w // 2, toolbar.height + 10), 
                          (frame_width // 2 + box_w // 2, toolbar.height + 45), (15, 15, 15), -1)
            cv2.rectangle(display_frame, (frame_width // 2 - box_w // 2, toolbar.height + 10), 
                          (frame_width // 2 + box_w // 2, toolbar.height + 45), COLORS["YELLOW"], 1)
            cv2.putText(display_frame, notification_text, (frame_width // 2 - box_w // 2 + 15, toolbar.height + 33), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS["YELLOW"], 1)

        cv2.imshow(WINDOW_TITLE, display_frame)

        # Keyboard shortcuts
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas_manager.clear()
            notification_text = "Canvas Cleared!"
            notification_timer = 45
        elif key == ord('s'):
            filename = canvas_manager.save_drawing()
            notification_text = f"Saved: {filename}"
            notification_timer = 90
        elif key in [ord('+'), ord('=')]:
            size_index = (size_index + 1) % len(BRUSH_SIZES)
            brush_thickness = BRUSH_SIZES[size_index]
            notification_text = f"Brush Size: {brush_thickness}px"
            notification_timer = 45
        elif key == ord('-'):
            size_index = (size_index - 1) % len(BRUSH_SIZES)
            brush_thickness = BRUSH_SIZES[size_index]
            notification_text = f"Brush Size: {brush_thickness}px"
            notification_timer = 45

    camera.release()
    cv2.destroyAllWindows()
    print("Application shut down cleanly.")

if __name__ == "__main__":
    main()
