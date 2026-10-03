# STAGE 9 & 10: Advanced Brush Features, Windows Pictures Saving & Studio UI
# Milestone:
# 1. Expanded Color Palette: RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE
# 2. Dynamic Brush Size Control: Touch [SIZE] button or press '+', '-' to change thickness
# 3. Save to Windows PHOTOS / PICTURES: Automatically exports directly to your Windows "Pictures/AirDrawing" folder!
# 4. Professional Studio UI: Modern dark toolbar, active tool preview widget, on-screen notifications

import cv2
import mediapipe as mp
import numpy as np
import math
import os
from datetime import datetime
from pathlib import Path

# 1. Directory Setup:
# Primary Save Target: User's Windows "Pictures/AirDrawing" folder (opens in Windows Photos app!)
PICTURES_DIR = os.path.join(Path.home(), "Pictures", "AirDrawing")
os.makedirs(PICTURES_DIR, exist_ok=True)

# Secondary Save Target: Project assets folder (for your GitHub portfolio showcase!)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 2. Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Persistent digital canvas
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Memory & smoothing
prev_x, prev_y = None, None
smooth_x, smooth_y = None, None
SMOOTHING_FACTOR = 0.65
STABILITY_THRESHOLD = 3
frames_since_draw = STABILITY_THRESHOLD

# Toolbar setup
TOOLBAR_HEIGHT = 75
BRUSH_SIZES = [4, 8, 14, 22]
size_index = 1
brush_thickness = BRUSH_SIZES[size_index]
eraser_thickness = 45

# 10 Toolbar Buttons
buttons = [
    {"name": "RED",    "color": (0, 0, 255),     "type": "color"},
    {"name": "GREEN",  "color": (0, 255, 0),     "type": "color"},
    {"name": "BLUE",   "color": (255, 0, 0),     "type": "color"},
    {"name": "YELLOW", "color": (0, 255, 255),   "type": "color"},
    {"name": "PURPLE", "color": (255, 0, 200),   "type": "color"},
    {"name": "ORANGE", "color": (0, 140, 255),   "type": "color"},
    {"name": "SIZE",   "color": (80, 80, 80),    "type": "size_toggle"},
    {"name": "ERASER", "color": (0, 0, 0),       "type": "eraser"},
    {"name": "SAVE",   "color": (120, 80, 0),    "type": "action_save"},
    {"name": "CLEAR",  "color": (40, 40, 40),    "type": "action_clear"}
]

btn_width = frame_width // len(buttons)
for i, btn in enumerate(buttons):
    btn["x1"] = i * btn_width + 3
    btn["x2"] = (i + 1) * btn_width - 3

current_color = (0, 255, 255)
current_tool_name = "YELLOW"
notification_text = "Welcome to Air Drawing Studio!"
notification_timer = 90
btn_click_cooldown = 0

def check_finger_states(lmList):
    """Vector alignment finger extension detector."""
    v1 = (lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
    v2 = (lmList[8].x - lmList[6].x, lmList[8].y - lmList[6].y)
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    cos_idx = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2) if (mag1 * mag2) > 0 else 0
    dist_tip_idx = math.hypot(lmList[8].x - lmList[5].x, lmList[8].y - lmList[5].y)
    dist_pip_idx = math.hypot(lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
    index_open = (cos_idx > 0.05) or (dist_tip_idx > dist_pip_idx * 1.05)

    v_m1 = (lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)
    v_m2 = (lmList[12].x - lmList[10].x, lmList[12].y - lmList[10].y)
    mag_m1 = math.hypot(v_m1[0], v_m1[1])
    mag_m2 = math.hypot(v_m2[0], v_m2[1])
    cos_mid = (v_m1[0]*v_m2[0] + v_m1[1]*v_m2[1]) / (mag_m1 * mag_m2) if (mag_m1 * mag_m2) > 0 else 0
    dist_tip_mid = math.hypot(lmList[12].x - lmList[9].x, lmList[12].y - lmList[9].y)
    dist_pip_mid = math.hypot(lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)
    middle_open = (cos_mid > 0.35) and (dist_tip_mid > dist_pip_mid * 1.3)

    return index_open, middle_open

def save_drawing():
    """Saves drawing to Windows Pictures/AirDrawing and creates a copy in assets/."""
    global notification_text, notification_timer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"air_drawing_{timestamp}.png"

    pictures_filepath = os.path.join(PICTURES_DIR, filename)
    assets_filepath = os.path.join(ASSETS_DIR, filename)

    # White digital paper background (255, 255, 255)
    white_paper = np.full((frame_height, frame_width, 3), 255, dtype=np.uint8)

    # 2D PIXEL MASK: Any pixel where at least one color channel is > 0
    # (Using 2D mask guarantees all 3 color channels transfer cleanly without turning white!)
    pixel_mask = np.any(canvas > 0, axis=-1)
    white_paper[pixel_mask] = canvas[pixel_mask]

    # Save to Windows Pictures folder (appears in Photos app!)
    cv2.imwrite(pictures_filepath, white_paper)

    # Save portfolio copy to project assets/ folder
    cv2.imwrite(assets_filepath, white_paper)

    notification_text = "Saved to Windows Pictures!"
    notification_timer = 90
    print(f"[SAVE] Exported artwork to: {pictures_filepath}")

print("=" * 70)
print("STAGE 9 & 10: Complete Air Drawing Studio Active!")
print(f"- Drawings save directly to: {PICTURES_DIR}")
print("- Touch [SAVE] or press 's' to export artwork")
print("- Touch [SIZE] or press '+', '-' to change brush size")
print("- Touch [CLEAR] or press 'c' to wipe canvas")
print("- Press 'q' to quit")
print("=" * 70)

while True:
    success, frame = camera.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    mode = "STANDBY"
    mode_color = (150, 150, 150)

    if btn_click_cooldown > 0:
        btn_click_cooldown -= 1

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = hand_landmarks.landmark
            index_open, middle_open = check_finger_states(lmList)

            raw_x = int(lmList[8].x * frame_width)
            raw_y = int(lmList[8].y * frame_height)

            if smooth_x is None or smooth_y is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = int(SMOOTHING_FACTOR * raw_x + (1 - SMOOTHING_FACTOR) * smooth_x)
                smooth_y = int(SMOOTHING_FACTOR * raw_y + (1 - SMOOTHING_FACTOR) * smooth_y)

            # Toolbar selection
            if smooth_y < TOOLBAR_HEIGHT:
                mode = "CHOOSING"
                mode_color = (255, 200, 0)
                prev_x, prev_y = None, None

                cv2.circle(frame, (smooth_x, smooth_y), 12, (255, 255, 255), 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, (0, 255, 255), cv2.FILLED)

                for btn in buttons:
                    if btn["x1"] <= smooth_x <= btn["x2"]:
                        if btn_click_cooldown == 0:
                            if btn["type"] == "color":
                                current_color = btn["color"]
                                current_tool_name = btn["name"]
                                notification_text = f"Color: {current_tool_name}"
                                notification_timer = 45

                            elif btn["type"] == "eraser":
                                current_color = (0, 0, 0)
                                current_tool_name = "ERASER"
                                notification_text = "Tool: ERASER"
                                notification_timer = 45

                            elif btn["type"] == "size_toggle":
                                size_index = (size_index + 1) % len(BRUSH_SIZES)
                                brush_thickness = BRUSH_SIZES[size_index]
                                notification_text = f"Brush Size: {brush_thickness}px"
                                notification_timer = 45
                                btn_click_cooldown = 15

                            elif btn["type"] == "action_save":
                                save_drawing()
                                btn_click_cooldown = 20

                            elif btn["type"] == "action_clear":
                                canvas.fill(0)
                                current_tool_name = "YELLOW"
                                current_color = (0, 255, 255)
                                notification_text = "Canvas Cleared!"
                                notification_timer = 45
                                btn_click_cooldown = 15

            # Canvas drawing / erasing
            elif index_open and not middle_open:
                mode = "ERASING" if current_tool_name == "ERASER" else "DRAWING"
                mode_color = (0, 200, 255) if current_tool_name == "ERASER" else (0, 255, 0)
                frames_since_draw = 0

                active_thick = eraser_thickness if current_tool_name == "ERASER" else brush_thickness

                if current_tool_name == "ERASER":
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2, (255, 255, 255), 2)
                    cv2.putText(frame, "E", (smooth_x - 5, smooth_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                else:
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2 + 2, current_color, cv2.FILLED)
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2 + 4, (255, 255, 255), 1)

                if prev_x is None or prev_y is None:
                    prev_x, prev_y = smooth_x, smooth_y
                    if current_tool_name == "ERASER":
                        cv2.circle(canvas, (smooth_x, smooth_y), active_thick // 2, (0, 0, 0), cv2.FILLED)
                else:
                    dist = math.hypot(smooth_x - prev_x, smooth_y - prev_y)
                    if dist < 180:
                        cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), current_color, active_thick)
                        if current_tool_name == "ERASER":
                            cv2.circle(canvas, (smooth_x, smooth_y), active_thick // 2, (0, 0, 0), cv2.FILLED)
                    prev_x, prev_y = smooth_x, smooth_y

            # Hover
            elif index_open and middle_open:
                mode = "HOVER (PEN UP)"
                mode_color = (255, 120, 0)
                prev_x, prev_y = None, None
                frames_since_draw = STABILITY_THRESHOLD

                cv2.circle(frame, (smooth_x, smooth_y), 16, (255, 255, 255), 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, (255, 255, 255), cv2.FILLED)

            else:
                frames_since_draw += 1
                if frames_since_draw < STABILITY_THRESHOLD and prev_x is not None:
                    active_thick = eraser_thickness if current_tool_name == "ERASER" else brush_thickness
                    cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), current_color, active_thick)
                    if current_tool_name == "ERASER":
                        cv2.circle(canvas, (smooth_x, smooth_y), active_thick // 2, (0, 0, 0), cv2.FILLED)
                    prev_x, prev_y = smooth_x, smooth_y
                else:
                    mode = "STANDBY"
                    mode_color = (150, 150, 150)
                    prev_x, prev_y = None, None

    else:
        frames_since_draw = STABILITY_THRESHOLD
        prev_x, prev_y = None, None
        smooth_x, smooth_y = None, None

    # Merge Canvas onto Camera Frame using 2D Pixel Mask
    pixel_mask = np.any(canvas > 0, axis=-1)
    display_frame = frame.copy()
    display_frame[pixel_mask] = canvas[pixel_mask]

    # Toolbar UI
    cv2.rectangle(display_frame, (0, 0), (frame_width, TOOLBAR_HEIGHT), (20, 20, 20), -1)
    cv2.line(display_frame, (0, TOOLBAR_HEIGHT), (frame_width, TOOLBAR_HEIGHT), (80, 80, 80), 2)

    for btn in buttons:
        x1, x2 = btn["x1"], btn["x2"]
        is_selected = (btn["name"] == current_tool_name)

        if btn["type"] == "color":
            cv2.rectangle(display_frame, (x1, 10), (x2, 65), btn["color"], -1)
            text_color = (0, 0, 0) if btn["name"] in ["YELLOW", "GREEN", "ORANGE"] else (255, 255, 255)
            cv2.putText(display_frame, btn["name"][:3], (x1 + 6, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 2)

        elif btn["type"] == "size_toggle":
            cv2.rectangle(display_frame, (x1, 10), (x2, 65), (55, 55, 55), -1)
            cv2.putText(display_frame, f"{brush_thickness}px", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        elif btn["type"] == "eraser":
            bg = (210, 210, 210) if is_selected else (60, 60, 60)
            txt_col = (0, 0, 0) if is_selected else (240, 240, 240)
            cv2.rectangle(display_frame, (x1, 10), (x2, 65), bg, -1)
            cv2.putText(display_frame, "ERAS", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, txt_col, 2)

        elif btn["type"] == "action_save":
            cv2.rectangle(display_frame, (x1, 10), (x2, 65), (140, 70, 0), -1)
            cv2.putText(display_frame, "SAVE", (x1 + 4, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        elif btn["type"] == "action_clear":
            cv2.rectangle(display_frame, (x1, 10), (x2, 65), (45, 45, 45), -1)
            cv2.putText(display_frame, "CLR", (x1 + 8, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 140, 255), 2)

        if is_selected:
            cv2.rectangle(display_frame, (x1 - 2, 7), (x2 + 2, 68), (255, 255, 255), 3)

    # Status Bar
    status_text = f"MODE: {mode} | TOOL: {current_tool_name} ({brush_thickness}px)"
    cv2.putText(display_frame, status_text, (15, frame_height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.52, mode_color, 2)

    # Floating Notification Banner
    if notification_timer > 0:
        notification_timer -= 1
        cv2.rectangle(display_frame, (frame_width // 2 - 160, TOOLBAR_HEIGHT + 10), 
                      (frame_width // 2 + 160, TOOLBAR_HEIGHT + 45), (15, 15, 15), -1)
        cv2.rectangle(display_frame, (frame_width // 2 - 160, TOOLBAR_HEIGHT + 10), 
                      (frame_width // 2 + 160, TOOLBAR_HEIGHT + 45), (0, 255, 255), 1)
        cv2.putText(display_frame, notification_text, (frame_width // 2 - 145, TOOLBAR_HEIGHT + 33), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow("Stage 9 & 10: Air Drawing Studio", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas.fill(0)
        prev_x, prev_y = None, None
        notification_text = "Canvas Cleared!"
        notification_timer = 45
    elif key == ord('s'):
        save_drawing()
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
print("Air Drawing Studio closed successfully.")
