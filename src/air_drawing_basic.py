# STAGE 6: Basic Air Drawing
# Milestone: Convert continuous index fingertip movement into persistent drawing strokes

import cv2
import mediapipe as mp
import numpy as np

# 1. Initialize MediaPipe
mp_hands = mp.solutions.hands
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

# Get camera dimensions
frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 3. Create a PERSISTENT digital canvas
# We create a black image (all zeros) with the exact same dimensions as our camera
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

# Variables to remember the previous fingertip position
prev_x, prev_y = None, None

# Drawing settings
brush_color = (0, 255, 255)  # Bright Yellow in BGR (Blue=0, Green=255, Red=255)
brush_thickness = 5

print("=" * 60)
print("STAGE 6: Air Drawing Active!")
print("- Move your index finger to draw in the air.")
print("- Press 'c' to clear the canvas.")
print("- Press 'q' to exit.")
print("=" * 60)

while True:
    success, frame = camera.read()
    if not success:
        break

    # Flip horizontally for natural mirror feel
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    curr_x, curr_y = None, None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract Index Fingertip (Landmark 8)
            index_tip = hand_landmarks.landmark[8]
            curr_x = int(index_tip.x * frame_width)
            curr_y = int(index_tip.y * frame_height)

            # Draw a pointer dot on the fingertip
            cv2.circle(frame, (curr_x, curr_y), 8, (0, 0, 255), cv2.FILLED)

            # Connect previous point to current point with a line
            if prev_x is None or prev_y is None:
                # First point of a new stroke: just record it
                prev_x, prev_y = curr_x, curr_y
            else:
                # Draw the line segment ON THE PERSISTENT CANVAS
                cv2.line(canvas, (prev_x, prev_y), (curr_x, curr_y), brush_color, brush_thickness)
                # Update previous position to current position
                prev_x, prev_y = curr_x, curr_y
    else:
        # Hand left the camera: reset previous point so it doesn't connect strokes
        prev_x, prev_y = None, None

    # 4. Merge Canvas onto the Camera Frame
    # Wherever our canvas has color (greater than 0), replace the camera pixel with the drawing
    drawn_pixels = canvas > 0
    display_frame = frame.copy()
    display_frame[drawn_pixels] = canvas[drawn_pixels]

    # Display HUD instruction bar
    cv2.putText(display_frame, "AIR DRAWING: Move index finger to draw | 'c': Clear | 'q': Quit", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # Display the final composite window
    cv2.imshow("Stage 6: Air Drawing", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        # Clear the canvas by resetting all pixels to 0 (black)
        canvas.fill(0)
        print("Canvas cleared!")

camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
