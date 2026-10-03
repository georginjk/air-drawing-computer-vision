# STAGE 3: OpenCV Fundamentals - Drawing on Video Frames
# Milestone: Learning to draw lines, circles, rectangles, and text live on camera

import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

print("=" * 60)
print("STAGE 3: OpenCV Drawing Fundamentals")
print("Look at your live feed to see shapes drawn on your camera window!")
print("Press 'q' to exit.")
print("=" * 60)

while True:
    success, frame = camera.read()
    if not success:
        break

    # Flip horizontally for natural mirror feel
    frame = cv2.flip(frame, 1)

    # 1. Understanding Frame Dimensions (Height, Width, Channels)
    # 'shape' returns (height, width, 3) where 3 is (Blue, Green, Red) channels
    h, w, c = frame.shape

    # 2. Draw a RECTANGLE (Simulating a future Toolbar button at the top!)
    # cv2.rectangle(image, top_left_corner, bottom_right_corner, color_bgr, thickness)
    # thickness=-1 fills the rectangle completely
    cv2.rectangle(frame, (20, 20), (220, 80), (50, 50, 50), -1)       # Dark gray box
    cv2.rectangle(frame, (20, 20), (220, 80), (0, 255, 255), 2)       # Yellow border

    # 3. Put TEXT inside the box
    # cv2.putText(image, text, (x, y), font, font_scale, color_bgr, thickness)
    cv2.putText(frame, "AIR DRAWING", (35, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 4. Draw a CIRCLE (This is exactly how we will highlight your fingertip in Stage 5!)
    # cv2.circle(image, center_coordinate, radius, color_bgr, thickness)
    # Let's draw a green circle at x=300, y=200
    target_x, target_y = 300, 200
    cv2.circle(frame, (target_x, target_y), 15, (0, 255, 0), cv2.FILLED)  # Filled green circle
    cv2.circle(frame, (target_x, target_y), 22, (255, 255, 255), 2)       # White outer ring

    # 5. Draw a LINE (This is how strokes will connect moving finger points in Stage 6!)
    # cv2.line(image, start_point, end_point, color_bgr, thickness)
    cv2.line(frame, (100, 350), (540, 350), (255, 0, 0), 4)              # Blue horizontal line

    # 6. Display the coordinate label on the screen
    coord_text = f"Target Point: ({target_x}, {target_y})"
    cv2.putText(frame, coord_text, (280, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Display the result
    cv2.imshow("Stage 3: OpenCV Fundamentals", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
print("Camera released. Window closed successfully.")
