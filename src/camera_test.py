# STAGE 2: First OpenCV Program - Webcam Live Feed
# Milestone: Python -> OpenCV -> Webcam -> Live Video Window

import cv2

# 1. Initialize the webcam
# 0 refers to the default built-in camera of your laptop / computer.
camera = cv2.VideoCapture(0)

# Optional safety check: Ensure camera opened successfully
if not camera.isOpened():
    print("Error: Could not open webcam. Check if another app is using it!")
    exit()

print("Webcam successfully started! Press 'q' on your keyboard to close the window.")

# 2. Continuous frame reading loop
while True:
    # Read one frame from the webcam
    # 'success' is True if the frame was read correctly
    # 'frame' is the actual image (grid of pixels)
    success, frame = camera.read()

    # If the camera fails to grab a frame, stop the loop safely
    if not success:
        print("Warning: Failed to grab frame from camera.")
        break

    # 3. Flip the frame horizontally (mirror view)
    # 1 means horizontal flip. This makes moving your hand left feel natural!
    frame = cv2.flip(frame, 1)

    # 4. Display the live frame in a desktop window named "Air Drawing - Camera Test"
    cv2.imshow("Air Drawing - Camera Test", frame)

    # 5. Wait for 1 millisecond and check if the user pressed the 'q' key
    # If 'q' is pressed, break out of the infinite while loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting camera feed...")
        break

# 6. Clean up resources
# Release the camera hardware so other applications can use it
camera.release()

# Close all OpenCV GUI windows
cv2.destroyAllWindows()
print("Camera released and all windows closed cleanly.")
