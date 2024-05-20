import cv2
import numpy as np
import mediapipe as mp
import traceback
from .vector_utils import (
    get_landmark_coordinates,
    compute_vertex,
    log_landmark,
    log_vertex,
    compute_inclination,
    compare_nums,
)
from .arm_state import ArmsState
from .leg_state import LegsState
from .facial_state import FacialState
from .event_handler import EventHandler
from .image_config import IMG_HEIGHT, IMG_WIDTH, UP_AREA_CONFIG

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


class BodyState:
    def __init__(self, body_config, EventHandler_config):
        self.draw_angles = body_config["draw_angles"]
        self.show_coords = body_config["show_coords"]

        self.EventHandler = EventHandler(**EventHandler_config)

        self.mode = None

        self.arms = ArmsState()
        self.legs = LegsState()
        self.face = FacialState()

        self.log = ""

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def calculate(self, image, results):
        # Extract pose landmarks
        try:
            if not results.pose_landmarks:
                return
            pose_landmarks = results.pose_landmarks.landmark

            # Get coordinates
            nose = get_landmark_coordinates(pose_landmarks, mp_pose.PoseLandmark.NOSE)

            left_eye = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_EYE
            )
            right_eye = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_EYE
            )

            left_ear = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_EAR
            )
            right_ear = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_EAR
            )

            mouth_left = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.MOUTH_LEFT
            )
            mouth_right = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.MOUTH_RIGHT
            )

            left_shoulder = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER
            )
            right_shoulder = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER
            )

            left_elbow = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_ELBOW
            )
            right_elbow = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW
            )

            left_wrist = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_WRIST
            )
            right_wrist = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST
            )

            left_pinky = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_PINKY
            )
            right_pinky = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_PINKY
            )

            left_index = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_INDEX
            )
            right_index = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_INDEX
            )

            left_thumb = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_THUMB
            )
            right_thumb = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_THUMB
            )

            left_hip = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_HIP
            )
            right_hip = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_HIP
            )

            left_knee = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_KNEE
            )
            right_knee = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_KNEE
            )

            left_ankle = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.LEFT_ANKLE
            )
            right_ankle = get_landmark_coordinates(
                pose_landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE
            )

            # Calculate angles
            left_shoulder_angle = compute_vertex(left_elbow, left_shoulder, left_hip)
            right_shoulder_angle = compute_vertex(
                right_elbow, right_shoulder, right_hip
            )

            left_elbow_angle = compute_vertex(left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = compute_vertex(
                right_shoulder, right_elbow, right_wrist
            )

            left_hip_angle = compute_vertex(left_shoulder, left_hip, left_knee)
            right_hip_angle = compute_vertex(right_shoulder, right_hip, right_knee)

            left_knee_angle = compute_vertex(left_hip, left_knee, left_ankle)
            right_knee_angle = compute_vertex(right_hip, right_knee, right_ankle)

            left_hip_knee_angle = compute_vertex(right_hip, left_hip, left_knee)
            right_hip_knee_angle = compute_vertex(left_hip, right_hip, right_knee)

            left_right_eyes_slope = compute_inclination(left_eye, right_eye)

            self.arms.update_arms_state(
                self.mode,
                image,
                self.EventHandler,
                nose,
                left_shoulder,
                right_shoulder,
                left_elbow,
                right_elbow,
                left_wrist,
                right_wrist,
                left_pinky,
                right_pinky,
                left_index,
                right_index,
                left_thumb,
                right_thumb,
                left_shoulder_angle,
                right_shoulder_angle,
                left_elbow_angle,
                right_elbow_angle,
            )
            self.legs.update_legs_state(
                self.mode,
                self.EventHandler,
                left_hip,
                right_hip,
                left_knee,
                right_knee,
                left_ankle,
                right_ankle,
                left_hip_angle,
                right_hip_angle,
                left_knee_angle,
                right_knee_angle,
            )
            self.face.update_state(
                self.mode,
                self.EventHandler,
                nose,
                left_eye,
                right_eye,
                left_ear,
                right_ear,
                mouth_left,
                mouth_right,
                left_shoulder,
                right_shoulder,
                left_right_eyes_slope,
            )

            # if (
            #     self.mode not in ["Driving"]
            #     and self.legs.left_up_state
            #     or self.legs.right_up_state
            # ):
            #     if (
            #         self.arms.left.straight
            #         and self.arms.left.up
            #         and self.arms.right.straight
            #         and self.arms.right.up
            #     ):
            #         self.EventHandler.add("down_walk")
            #     elif (
            #         self.arms.left.straight
            #         and self.arms.left.up
            #         and not self.arms.right.up
            #     ):
            #         if compare_nums(right_wrist[0], nose[0], "gt"):
            #             self.EventHandler.add("left_walk_both")
            #         else:
            #             self.EventHandler.add("left_walk")
            #     elif (
            #         self.arms.right.straight
            #         and self.arms.right.up
            #         and not self.arms.left.up
            #     ):
            #         if compare_nums(left_wrist[0], nose[0], "lt"):
            #             self.EventHandler.add("right_walk_both")
            #         else:
            #             self.EventHandler.add("right_walk")
            #     else:
            #         self.EventHandler.add("walk")

            angles = (
                (left_shoulder_angle, left_shoulder),
                (right_shoulder_angle, right_shoulder),
                (left_elbow_angle, left_elbow),
                (right_elbow_angle, right_elbow),
                (left_hip_angle, left_hip),
                (right_hip_angle, right_hip),
                (left_knee_angle, left_knee),
                (right_knee_angle, right_knee),
            )

            if self.mode == "Driving":
                cv2.rectangle(
                    image,
                    (UP_AREA_CONFIG["x"], UP_AREA_CONFIG["y"]),
                    (
                        UP_AREA_CONFIG["x"] + UP_AREA_CONFIG["width"],
                        UP_AREA_CONFIG["y"] + UP_AREA_CONFIG["height"],
                    ),
                    (0, 255, 0),
                    2,
                )

            if self.draw_angles:
                for (angle, landmark) in angles:
                    cv2.putText(
                        image,
                        str(round(angle, None)),
                        tuple(np.multiply(landmark[:2], [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

            if self.show_coords:
                self.log = f"""
nose:            {log_landmark(nose)}
left_eye:        {log_landmark(left_eye)}              right_eye:       {log_landmark(right_eye)}
left_ear:        {log_landmark(left_ear)}              right_ear:       {log_landmark(right_ear)}
mouth_left:      {log_landmark(mouth_left)}            mouth_right:     {log_landmark(mouth_right)}
left_shoulder:   {log_landmark(left_shoulder)}         right_shoulder:  {log_landmark(right_shoulder)}
left_elbow:      {log_landmark(left_elbow)}            right_elbow:     {log_landmark(right_elbow)}
left_wrist:      {log_landmark(left_wrist)}            right_wrist:     {log_landmark(right_wrist)}
left_pinky:      {log_landmark(left_pinky)}            right_pinky:     {log_landmark(right_pinky)}
left_index:      {log_landmark(left_index)}            right_index:     {log_landmark(right_index)}
left_thumb:      {log_landmark(left_thumb)}            right_thumb:     {log_landmark(right_thumb)}
left_hip:        {log_landmark(left_hip)}              right_hip:       {log_landmark(right_hip)}
left_knee:       {log_landmark(left_knee)}             right_knee:      {log_landmark(right_knee)}
left_ankle:      {log_landmark(left_ankle)}            right_ankle:     {log_landmark(right_ankle)}

lr_eyes_slope:        {log_vertex(left_right_eyes_slope)}
left_shoulder_angle:  {log_vertex(left_shoulder_angle)}   right_shoulder_angle: {log_vertex(right_shoulder_angle)}
left_elbow_angle:     {log_vertex(left_elbow_angle)}      right_elbow_angle:    {log_vertex(right_elbow_angle)}
left_hip_angle:       {log_vertex(left_hip_angle)}        right_hip_angle:      {log_vertex(right_hip_angle)}
left_knee_angle:      {log_vertex(left_knee_angle)}       right_knee_angle:     {log_vertex(right_knee_angle)}
left_hip_knee_angle:  {log_vertex(left_hip_knee_angle)}   right_hip_knee_angle: {log_vertex(right_hip_knee_angle)}
--------------------------------------------------------------------
"""
            else:
                self.log = ""

        except Exception:
            print(traceback.format_exc())

    def __str__(self):
        left_arm = self.arms.left_arm
        right_arm = self.arms.right_arm
        left_leg = self.legs.left_leg
        right_leg = self.legs.right_leg

        return f"""{self.log}
Walk: {self.legs}
Left arm: {left_arm}
Right arm: {right_arm}
Left leg: {left_leg}
Right leg: {right_leg}
Face: {self.face}
--------------------------------------------------------------------
Keyboard: {'YES' if self.EventHandler.keyboard_active else 'NO'}       Cross cmd: {'YES' if self.EventHandler.cross_cmd_active else 'NO'}
{self.EventHandler}
"""
