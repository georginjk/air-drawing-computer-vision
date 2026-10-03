# STAGE 11: Modular Architecture - Hand Tracking Module
# Encapsulates Google MediaPipe and Vector Angle Finger Detection.

import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.6, track_con=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )

    def find_hands(self, frame, draw=True):
        """Processes RGB frame and returns raw landmarks list."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                return hand_landmarks.landmark
        return None

    def get_pixel_coords(self, landmark, frame_width, frame_height):
        """Converts normalized landmark coordinates to screen pixel coordinates."""
        return int(landmark.x * frame_width), int(landmark.y * frame_height)

    def check_finger_states(self, lmList):
        """
        Uses Vector Alignment (Cosine of bone angles) to determine finger extension:
        - index_open: True if index finger is extended forward
        - middle_open: True if middle finger is extended forward
        """
        # --- INDEX FINGER (MCP: 5, PIP: 6, TIP: 8) ---
        v1 = (lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
        v2 = (lmList[8].x - lmList[6].x, lmList[8].y - lmList[6].y)
        mag1 = math.hypot(v1[0], v1[1])
        mag2 = math.hypot(v2[0], v2[1])
        cos_idx = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2) if (mag1 * mag2) > 0 else 0
        dist_tip_idx = math.hypot(lmList[8].x - lmList[5].x, lmList[8].y - lmList[5].y)
        dist_pip_idx = math.hypot(lmList[6].x - lmList[5].x, lmList[6].y - lmList[5].y)
        index_open = (cos_idx > 0.05) or (dist_tip_idx > dist_pip_idx * 1.05)

        # --- MIDDLE FINGER (MCP: 9, PIP: 10, TIP: 12) ---
        v_m1 = (lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)
        v_m2 = (lmList[12].x - lmList[10].x, lmList[12].y - lmList[10].y)
        mag_m1 = math.hypot(v_m1[0], v_m1[1])
        mag_m2 = math.hypot(v_m2[0], v_m2[1])
        cos_mid = (v_m1[0]*v_m2[0] + v_m1[1]*v_m2[1]) / (mag_m1 * mag_m2) if (mag_m1 * mag_m2) > 0 else 0
        dist_tip_mid = math.hypot(lmList[12].x - lmList[9].x, lmList[12].y - lmList[9].y)
        dist_pip_mid = math.hypot(lmList[10].x - lmList[9].x, lmList[10].y - lmList[9].y)
        middle_open = (cos_mid > 0.35) and (dist_tip_mid > dist_pip_mid * 1.3)

        return index_open, middle_open
