# STAGE 8 (PERFECTED): Seamless Color & Eraser Selection Toolbar
# Fixes:
# 1. Dynamic Button Widths: Automatically scales to ANY camera resolution (640, 720, 1080p)
# 2. Universal Selection: Select buttons with EITHER 1 finger OR 2 fingers in the toolbar!
# 3. Dedicated Eraser Engine: Uses cv2.circle + cv2.line to guarantee instant, clean erasure
# 4. Added on-screen [CLEAR] button to wipe the whole screen without touching keyboard

import cv2
import mediapipe as mp
import numpy as np
import math

# 1. Initialize MediaPipe
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

# Persistent digital canvas (starts black)
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Memory for drawing & smoothing
prev_x, prev_y = None, None
smooth_x, smooth_y = None, None
SMOOTHING_FACTOR = 0.65
STABILITY_THRESHOLD = 3
frames_since_draw = STABILITY_THRESHOLD

# --- TOOLBAR SETUP ---
TOOLBAR_HEIGHT = 80

# 6 Clean Buttons: RED, GREEN, BLUE, YELLOW, ERASER, CLEAR ALL
# Dynamically sized to fill the screen width evenly!
num_buttons = 6
btn_width = frame_width // num_buttons

buttons = [
    {"name": "RED",    "color": (0, 0, 255),     "type": "color"},
    {"name": "GREEN",  "color": (0, 255, 0),     "type": "color"},
    {"name": "BLUE",   "color": (255, 0, 0),     "type": "color"},
    {"name": "YELLOW", "color": (0, 255, 255),   "type": "color"},
    {"name": "ERASER", "color": (0, 0, 0),       "type": "eraser"},
    {"name": "CLEAR",  "color": (40, 40, 40),    "type": "action"}
]

# Calculate x1, x2 for each button
for i, btn in enumerate(buttons):
    btn["x1"] = i * btn_width + 5
    btn["x2"] = (i + 1) * btn_width - 5

# Active drawing state
current_color = (0, 255, 255)   # Default: Yellow
current_tool_name = "YELLOW"
brush_thickness = 6
eraser_thickness = 45           # Generous eraser diameter (45 pixels)

def check_finger_states(lmList):
    """Checks Index and Middle finger extension using Vector Alignment."""
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

print("=" * 65)
print("STAGE 8 (PERFECTED): Air Drawing Toolbar with Rock-Solid Eraser")
print("- Touch ANY button in the top toolbar to select it (with 1 or 2 fingers)")
print("- ☝️  1 Finger on Canvas: DRAW or ERASE")
print("- ✌️  2 Fingers on Canvas: HOVER (Move pointer freely)")
print("- Select [CLEAR] button or press 'c' to wipe canvas")
print("- Press 'q' to quit")
print("=" * 65)

while True:
    success, frame = camera.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    mode = "STANDBY"
    mode_color = (150, 150, 150)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = hand_landmarks.landmark
            index_open, middle_open = check_finger_states(lmList)

            raw_x = int(lmList[8].x * frame_width)
            raw_y = int(lmList[8].y * frame_height)

            # Smoothing
            if smooth_x is None or smooth_y is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = int(SMOOTHING_FACTOR * raw_x + (1 - SMOOTHING_FACTOR) * smooth_x)
                smooth_y = int(SMOOTHING_FACTOR * raw_y + (1 - SMOOTHING_FACTOR) * smooth_y)

            # --- UNIVERSAL TOOLBAR SELECTION (Works with 1 OR 2 fingers!) ---
            if smooth_y < TOOLBAR_HEIGHT:
                mode = "CHOOSING TOOL"
                mode_color = (255, 200, 0)
                prev_x, prev_y = None, None  # Never draw inside toolbar

                # Reticle circle on fingertip
                cv2.circle(frame, (smooth_x, smooth_y), 15, (255, 255, 255), 2)
                cv2.circle(frame, (smooth_x, smooth_y), 5, (0, 255, 255), cv2.FILLED)

                # Check which button was touched
                for btn in buttons:
                    if btn["x1"] <= smooth_x <= btn["x2"]:
                        if btn["type"] == "color":
                            current_color = btn["color"]
                            current_tool_name = btn["name"]
                        elif btn["type"] == "eraser":
                            current_color = (0, 0, 0)
                            current_tool_name = "ERASER"
                        elif btn["type"] == "action" and btn["name"] == "CLEAR":
                            canvas.fill(0)
                            current_tool_name = "YELLOW"
                            current_color = (0, 255, 255)

            # --- CANVAS DRAWING / ERASING (Below Toolbar) ---
            elif index_open and not middle_open:
                # ☝️ 1 FINGER: DRAW OR ERASE
                mode = "ERASING" if current_tool_name == "ERASER" else "DRAWING"
                mode_color = (0, 200, 255) if current_tool_name == "ERASER" else (0, 255, 0)
                frames_since_draw = 0

                active_thick = eraser_thickness if current_tool_name == "ERASER" else brush_thickness

                # Cursor marker
                if current_tool_name == "ERASER":
                    # Distinct hollow white ring for eraser
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2, (255, 255, 255), 2)
                    cv2.putText(frame, "E", (smooth_x - 6, smooth_y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                else:
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2 + 3, current_color, cv2.FILLED)
                    cv2.circle(frame, (smooth_x, smooth_y), active_thick // 2 + 5, (255, 255, 255), 2)

                # Draw / Erase on persistent canvas
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

            elif index_open and middle_open:
                # ✌️ 2 FINGERS: HOVER / PEN UP (Reposition without drawing or erasing)
                mode = "HOVER (PEN UP)"
                mode_color = (255, 120, 0)
                prev_x, prev_y = None, None
                frames_since_draw = STABILITY_THRESHOLD

                cv2.circle(frame, (smooth_x, smooth_y), 16, (255, 255, 255), 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, (255, 255, 255), cv2.FILLED)

            else:
                # Standby / debounced finish
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

    # Merge Canvas onto Camera Feed
    drawn_pixels = canvas > 0
    display_frame = frame.copy()
    display_frame[drawn_pixels] = canvas[drawn_pixels]

    # --- RENDER TOP TOOLBAR ---
    cv2.rectangle(display_frame, (0, 0), (frame_width, TOOLBAR_HEIGHT), (25, 25, 25), -1)
    cv2.line(display_frame, (0, TOOLBAR_HEIGHT), (frame_width, TOOLBAR_HEIGHT), (120, 120, 120), 2)

    for btn in buttons:
        x1, x2 = btn["x1"], btn["x2"]
        is_selected = (btn["name"] == current_tool_name)

        if btn["type"] == "eraser":
            btn_bg = (200, 200, 200) if is_selected else (60, 60, 60)
            text_color = (0, 0, 0) if is_selected else (240, 240, 240)
            cv2.rectangle(display_frame, (x1, 10), (x2, 70), btn_bg, -1)
            cv2.putText(display_frame, "ERASER", (x1 + 10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)
        elif btn["type"] == "action":
            cv2.rectangle(display_frame, (x1, 10), (x2, 70), (50, 50, 50), -1)
            cv2.putText(display_frame, "CLEAR", (x1 + 15, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)
        else:
            cv2.rectangle(display_frame, (x1, 10), (x2, 70), btn["color"], -1)
            text_color = (0, 0, 0) if btn["name"] in ["YELLOW", "GREEN"] else (255, 255, 255)
            cv2.putText(display_frame, btn["name"], (x1 + 15, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)

        # Draw a bold glowing highlight around the currently selected button
        if is_selected:
            cv2.rectangle(display_frame, (x1 - 2, 8), (x2 + 2, 72), (255, 255, 255), 3)

    # Status Bar
    status_text = f"MODE: {mode} | ACTIVE TOOL: {current_tool_name}"
    cv2.putText(display_frame, status_text, (15, frame_height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, mode_color, 2)

    cv2.imshow("Stage 8: Air Drawing with Toolbar", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas.fill(0)
        prev_x, prev_y = None, None
        print("Canvas wiped clean!")

camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
