from .event_handler import EventHandler
from .vector_utils import get_side_orientation


class FacialState:

    MAX_TILT_ANGLE = 35

    def __init__(self):
        self.tilt_direction = None
        self.side_facing = None

    def update_state(
        self,
        event_handler: EventHandler,
        nose,
        left_eye,
        right_eye,
        left_ear,
        right_ear,
        mouth_left,
        mouth_right,
        left_shoulder,
        right_shoulder,
        eye_slope_angle,
    ):
        if eye_slope_angle > self.MAX_TILT_ANGLE:
            self.tilt_direction = "left"
            event_handler.add_command("face_tilt_left")
        elif eye_slope_angle < -self.MAX_TILT_ANGLE:
            self.tilt_direction = "right"
            event_handler.add_command("face_tilt_right")
        else:
            self.tilt_direction = None

        self.side_facing = get_side_orientation(
            [[right_ear, left_ear], [right_shoulder, left_shoulder]]
        )

    def __str__(self):
        return f"Side facing: {self.side_facing}"
