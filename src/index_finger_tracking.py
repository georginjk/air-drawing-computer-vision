# STAGE 5: Index Finger Tracking
# Milestone: Track index fingertip (Landmark 8), convert to screen pixel coordinates,
#            draw a glowing circle on the tip, and display live (x, y) coordinates.

import cv2
import mediapipe as mp

# 1. Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# 2. Start webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

print("=" * 60)
print("STAGE 5: Index Fingertip Tracking Active!")
print("Move your index finger around to see the target circle follow it.")
print("Press 'q' to exit.")
print("=" * 60)

while True:
    success, frame = camera.read()
    if not success:
        break

    # Flip horizontally for natural mirror feel
    frame = cv2.flip(frame, 1)

    # Frame dimensions: height (h) and width (w) in pixels
    h, w, c = frame.shape

    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Variable to store current index fingertip position
    fingertip_pos = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the hand skeleton faintly in the background
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # --- LANDMARK 8: INDEX FINGER TIP ---
            # MediaPipe gives normalized coordinates (0.0 to 1.0)
            index_tip = hand_landmarks.landmark[8]

            # Convert normalized ratio to actual screen pixel coordinates:
            tip_x = int(index_tip.x * w)
            tip_y = int(index_tip.y * h)
            fingertip_pos = (tip_x, tip_y)

            # Draw a glowing target circle right on your index fingertip!
            # Solid magenta center
            cv2.circle(frame, (tip_x, tip_y), 12, (255, 0, 255), cv2.FILLED)
            # White outer ring
            cv2.circle(frame, (tip_x, tip_y), 18, (255, 255, 255), 2)

    # Display an information HUD (Heads-Up Display) box at top-left
    cv2.rectangle(frame, (20, 20), (340, 80), (30, 30, 30), -1)
    cv2.rectangle(frame, (20, 20), (340, 80), (255, 0, 255), 2)

    if fingertip_pos is not None:
        coord_text = f"Index Tip: ({fingertip_pos[0]}, {fingertip_pos[1]})"
        cv2.putText(frame, coord_text, (35, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "Hand not detected", (35, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)

    # Display video
    cv2.imshow("Stage 5: Index Finger Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
