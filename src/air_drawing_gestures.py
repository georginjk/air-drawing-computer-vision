# STAGE 7 (MASTERED): Debounced Continuous Gesture Air Drawing
# Fixes the dashed-line issue on angled curves (e.g. left side of heart):
# 1. Stroke Debouncing (Hysteresis Buffer): Prevents 1-frame sensor flickers from breaking strokes
# 2. Angle-Tolerant Index Extension: Works smoothly across all angles, curves, and tilts
# 3. Dedicated Middle-Finger Gate: Keeps Middle cleanly CLOSED without requiring stiff fingers

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

# Persistent digital canvas
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Memory for drawing & smoothing
prev_x, prev_y = None, None
smooth_x, smooth_y = None, None
SMOOTHING_FACTOR = 0.65

# Stroke Debounce Buffer (Prevents dashed lines during quick curves)
# Keeps the stroke alive if a single frame drops tracking
STABILITY_THRESHOLD = 3
frames_since_draw = STABILITY_THRESHOLD

# Brush settings
brush_color = (0, 255, 255)  # Bright Yellow
brush_thickness = 6

def check_finger_states(lmList):
    """
    Evaluates finger states with angle tolerance for fluid drawing:
    - Index: Open as long as it's not curled backwards into palm
    - Middle: Requires clear forward extension to trigger Hover
    """
    # --- INDEX FINGER (Knuckle 5, Joint 6, Tip 8) ---
    v1 = (lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
    v2 = (lmList[8].x - lmList[6].x, lmList[8].y - lmList[6].y)
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    cos_index = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2) if (mag1 * mag2) > 0 else 0
    dist_tip_idx = math.hypot(lmList[8].x - lmList[5].x, lmList[8].y - lmList[5].y)
    dist_pip_idx = math.hypot(lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
    
    # Angle-tolerant: Index is open if pointing forward or tip extended
    index_open = (cos_index > 0.05) or (dist_tip_idx > dist_pip_idx * 1.05)

    # --- MIDDLE FINGER (Knuckle 9, Joint 10, Tip 12) ---
    v_m1 = (lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)
    v_m2 = (lmList[12].x - lmList[10].x, lmList[12].y - lmList[10].y)
    mag_m1 = math.hypot(v_m1[0], v_m1[1])
    mag_m2 = math.hypot(v_m2[0], v_m2[1])
    cos_middle = (v_m1[0]*v_m2[0] + v_m1[1]*v_m2[1]) / (mag_m1 * mag_m2) if (mag_m1 * mag_m2) > 0 else 0
    dist_tip_mid = math.hypot(lmList[12].x - lmList[9].x, lmList[12].y - lmList[9].y)
    dist_pip_mid = math.hypot(lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)

    # Middle requires distinct forward extension (peace sign)
    middle_open = (cos_middle > 0.35) and (dist_tip_mid > dist_pip_mid * 1.3)

    return index_open, middle_open

print("=" * 65)
print("STAGE 7 (MASTERED): Debounced Continuous Gesture Air Drawing")
print("- ☝️  INDEX EXTENDED: DRAW (Solid continuous curves in all directions)")
print("- ✌️  INDEX + MIDDLE: HOVER / PEN UP (Lifts pen cleanly)")
print("- ✊ FIST / RELAXED: STANDBY")
print("- Press 'c' to clear | Press 'q' to quit")
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
    index_state = "CLOSED"
    middle_state = "CLOSED"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = hand_landmarks.landmark

            # Draw subtle skeleton
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_open, middle_open = check_finger_states(lmList)

            index_state = "OPEN" if index_open else "CLOSED"
            middle_state = "OPEN" if middle_open else "CLOSED"

            raw_x = int(lmList[8].x * frame_width)
            raw_y = int(lmList[8].y * frame_height)

            # Anti-Jitter Smoothing
            if smooth_x is None or smooth_y is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = int(SMOOTHING_FACTOR * raw_x + (1 - SMOOTHING_FACTOR) * smooth_x)
                smooth_y = int(SMOOTHING_FACTOR * raw_y + (1 - SMOOTHING_FACTOR) * smooth_y)

            # --- GESTURE LOGIC WITH DEBOUNCING ---
            if index_open and not middle_open:
                # ☝️ 1 Finger: DRAW MODE
                mode = "DRAWING"
                mode_color = (0, 255, 0)
                frames_since_draw = 0  # Reset debounce timer

                cv2.circle(frame, (smooth_x, smooth_y), 9, brush_color, cv2.FILLED)
                cv2.circle(frame, (smooth_x, smooth_y), 13, (255, 255, 255), 2)

                if prev_x is None or prev_y is None:
                    prev_x, prev_y = smooth_x, smooth_y
                else:
                    dist = math.hypot(smooth_x - prev_x, smooth_y - prev_y)
                    if dist < 180:
                        cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), brush_color, brush_thickness)
                    prev_x, prev_y = smooth_x, smooth_y

            elif index_open and middle_open:
                # ✌️ 2 Fingers: HOVER MODE (LIFT PEN)
                mode = "HOVER (PEN UP)"
                mode_color = (255, 120, 0)
                frames_since_draw = STABILITY_THRESHOLD

                prev_x, prev_y = None, None

                cv2.circle(frame, (smooth_x, smooth_y), 16, (255, 255, 255), 2)
                cv2.circle(frame, (smooth_x, smooth_y), 4, (255, 255, 255), cv2.FILLED)

            else:
                # Temporary glitch or intentional fist?
                frames_since_draw += 1
                if frames_since_draw < STABILITY_THRESHOLD and prev_x is not None:
                    # Debounce grace: keep drawing mode alive across 1-2 momentary frame drops!
                    mode = "DRAWING"
                    mode_color = (0, 255, 0)
                    cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), brush_color, brush_thickness)
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

    # HUD Box
    cv2.rectangle(display_frame, (15, 15), (380, 85), (25, 25, 25), -1)
    cv2.rectangle(display_frame, (15, 15), (380, 85), mode_color, 2)
    cv2.putText(display_frame, f"MODE: {mode}", (25, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.75, mode_color, 2)
    cv2.putText(display_frame, f"Index: {index_state} | Middle: {middle_state}", 
                (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.putText(display_frame, "1 Finger: Draw | 2 Fingers: Hover | 'c': Clear | 'q': Quit",
                (15, frame_height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)

    cv2.imshow("Stage 7: Gesture Air Drawing", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas.fill(0)
        prev_x, prev_y = None, None
        frames_since_draw = STABILITY_THRESHOLD
        print("Canvas wiped clean!")

camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
