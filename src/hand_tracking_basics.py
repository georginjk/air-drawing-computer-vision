# STAGE 4: MediaPipe Hand Tracking
# Milestone: Webcam -> MediaPipe -> Hand Detected -> 21 Hand Landmarks & Skeleton Displayed

import cv2
import mediapipe as mp

# 1. Initialize MediaPipe Hands solution
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Create our hand detector:
# - max_num_hands=1: Track only one hand initially (for simpler air drawing)
# - min_detection_confidence=0.7: 70% confidence needed to confirm a hand is detected
# - min_tracking_confidence=0.5: 50% confidence needed to keep tracking the hand
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
print("STAGE 4: MediaPipe Hand Tracking Active!")
print("Wave your hand in front of the camera to see the 21 joints tracked live.")
print("Press 'q' to exit.")
print("=" * 60)

while True:
    success, frame = camera.read()
    if not success:
        break

    # Flip horizontally for natural mirror feel
    frame = cv2.flip(frame, 1)

    # 3. MediaPipe requires RGB images, but OpenCV reads in BGR!
    # Convert BGR to RGB so the AI model can understand it:
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 4. Process the frame with the MediaPipe AI model
    results = hands.process(rgb_frame)

    # 5. Check if any hand was detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the 21 landmark dots and connecting lines (skeleton)
            mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS
            )

    # Display the result in a window
    cv2.imshow("Stage 4: Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up resources
camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
