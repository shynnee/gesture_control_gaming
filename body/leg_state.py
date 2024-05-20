from .event_handler import EventHandler


class SingleLegState:
    def __init__(self, side):
        self.side = side
        self.is_straight = None

    def update_leg_state(self, event_handler: EventHandler, hip, knee, ankle, hip_angle, knee_angle):
        self.is_straight = knee_angle > 160

    def __str__(self):
        states = ("straight" if self.is_straight else "",)
        states = filter(lambda s: s != "", states)
        return ", ".join(states)


class LegsState:

    MAX_KNEE_ANGLE_UP = 155
    MIN_KNEE_VISIBILITY = 0.5

    def __init__(self):
        self.left_leg = SingleLegState("left")
        self.right_leg = SingleLegState("right")

        self.is_left_leg_up = False
        self.is_right_leg_up = False
        self.is_squatting = False
        self.step_count = 0

    def update_legs_state(
        self,
        event_handler: EventHandler,
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
    ):
        self.left_leg.update_leg_state(
            event_handler,
            left_hip,
            left_knee,
            left_ankle,
            left_hip_angle,
            left_knee_angle,
        )
        self.right_leg.update_leg_state(
            event_handler,
            right_hip,
            right_knee,
            right_ankle,
            right_hip_angle,
            right_knee_angle,
        )

        if (
            left_knee[3] > self.MIN_KNEE_VISIBILITY
            and right_knee[3] > self.MIN_KNEE_VISIBILITY
        ):
            if (
                left_knee_angle < self.MAX_KNEE_ANGLE_UP
                and right_knee_angle < self.MAX_KNEE_ANGLE_UP
            ):
                if not self.is_squatting:
                    self.is_squatting = True
                    event_handler.add_command("squat")
            else:
                self.is_squatting = False

            if self.is_squatting:
                return

            if left_knee_angle < self.MAX_KNEE_ANGLE_UP:
                if not self.is_left_leg_up:
                    self.is_left_leg_up = True
                    self.step_count += 1
            else:
                self.is_left_leg_up = False

            if right_knee_angle < self.MAX_KNEE_ANGLE_UP:
                if not self.is_right_leg_up:
                    self.is_right_leg_up = True
                    self.step_count += 1
            else:
                self.is_right_leg_up = False

    def __str__(self):
        return f"steps: {self.step_count}"
