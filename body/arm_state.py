import cv2
from .event_handler import EventHandler
from .vector_utils import (
    compare_nums,
    is_landmarks_enclosed,
    compute_inclination,
    compute_separation,
    in_range,
    is_landmarks_in_bounds,
)
from .image_config import IMG_HEIGHT, IMG_WIDTH, UP_AREA_CONFIG


class SingleArmState:

    MAX_CURL_ANGLE = 45

    def __init__(self, side):
        self.side = side
        self.is_straight = None
        self.is_curled = None
        self.is_raised_up = None
        self.is_in_front = None
        self.is_lifted = None

    @property
    def is_left_arm(self):
        return self.side == "left"

    def update_arm_state(
        self,
        event_handler: EventHandler,
        shoulder,
        elbow,
        wrist,
        pinky,
        index,
        thumb,
        shoulder_angle,
        elbow_angle,
    ):
        self.is_straight = elbow_angle > 160
        self.is_raised_up = shoulder_angle > 45
        self.is_in_front = wrist[2] > shoulder[2]
        self.is_curled = elbow_angle < self.MAX_CURL_ANGLE
        self.is_lifted = wrist[1] < shoulder[1]

    def __str__(self):
        states = (
            "straight" if self.is_straight else "",
            "curled" if self.is_curled else "",
            "up" if self.is_raised_up else "down",
            "front" if self.is_in_front else "back",
        )
        states = filter(lambda s: s != "", states)
        return ", ".join(states)


class ArmsState:

    MAX_ELBOW_CROSS_ANGLE = 60
    DRIVING_SLOPE_ANGLE = 25

    def __init__(self):
        self.left_arm = SingleArmState("left")
        self.right_arm = SingleArmState("right")

        self.are_arms_crossed = None
        self.is_left_swinging = None
        self.is_left_swinging_up = None
        self.is_right_swinging = None
        self.is_right_swinging_up = None
        self.are_hands_held = None
        self.are_driving_hands = None

    def update_arms_state(
        self,
        mode: str,
        image,
        event_handler: EventHandler,
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
    ):
        self.left_arm.update_arm_state(
            event_handler,
            left_shoulder,
            left_elbow,
            left_wrist,
            left_pinky,
            left_index,
            left_thumb,
            left_shoulder_angle,
            left_elbow_angle,
        )
        self.right_arm.update_arm_state(
            event_handler,
            right_shoulder,
            right_elbow,
            right_wrist,
            right_pinky,
            right_index,
            right_thumb,
            right_shoulder_angle,
            right_elbow_angle,
        )

        left_right_hands_slope = compute_inclination(left_thumb, right_thumb)

        if mode == "Driving":
            if is_landmarks_enclosed(
                [
                    left_pinky,
                    right_pinky,
                    left_index,
                    right_index,
                    left_thumb,
                    right_thumb,
                ],
                0.3,
            ):
                self.are_driving_hands = True

                cv2.circle(
                    image,
                    (
                        int((left_thumb[0] + right_thumb[0]) / 2 * IMG_WIDTH),
                        int((left_thumb[1] + right_thumb[1]) / 2 * IMG_HEIGHT),
                    ),
                    50,
                    (255, 0, 0),
                    5,
                )

                # Both hands are in the driving up area
                if is_landmarks_in_bounds(
                    [
                        left_pinky,
                        right_pinky,
                        left_index,
                        right_index,
                        left_thumb,
                        right_thumb,
                    ],
                    **UP_AREA_CONFIG,
                ):
                    event_handler.add_command("d2_driving_up")

                if left_right_hands_slope > self.DRIVING_SLOPE_ANGLE:
                    event_handler.add_command("d1_driving_left")
                elif left_right_hands_slope < -self.DRIVING_SLOPE_ANGLE:
                    event_handler.add_command("d1_driving_right")
                else:
                    event_handler.add_command("d1_driving_default")
            else:
                self.are_driving_hands = False

            return

        if (
            compare_nums(left_wrist[0], right_wrist[0], "lt")
            and left_elbow_angle < self.MAX_ELBOW_CROSS_ANGLE
            and right_elbow_angle < self.MAX_ELBOW_CROSS_ANGLE
        ):
            if not self.are_arms_crossed:
                self.are_arms_crossed = True
                event_handler.add_command("cross")
        else:
            self.are_arms_crossed = False

        if self.are_arms_crossed:
            return

        if compare_nums(left_wrist[0], nose[0], "lt"):
            if not self.is_left_swinging:
                self.is_left_swinging = True
                event_handler.add_command(f"left_swing{'_hold' if self.right_arm.is_lifted else ''}")
        else:
            self.is_left_swinging = False

        if compare_nums(left_wrist[0], nose[0], "gt") and self.left_arm.is_lifted:
            if not self.is_left_swinging_up:
                self.is_left_swinging_up = True
                event_handler.add_command("left_swing_up")
        else:
            self.is_left_swinging_up = False

        if compare_nums(right_wrist[0], nose[0], "gt"):
            if not self.is_right_swinging:
                self.is_right_swinging = True
                event_handler.add_command(f"right_swing{'_hold' if self.left_arm.is_lifted else ''}")
        else:
            self.is_right_swinging = False

        if compare_nums(right_wrist[0], nose[0], "lt") and self.right_arm.is_lifted:
            if not self.is_right_swinging_up:
                self.is_right_swinging_up = True
                event_handler.add_command("right_swing_up")
        else:
            self.is_right_swinging_up = False

    def __str__(self):
        return f""
