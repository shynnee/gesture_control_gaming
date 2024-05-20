from .key_command_manager import KeyCommandManager


class EventHandler:
    def __init__(
        self,
        keyboard_active,
        cross_cmd_active,
        default_timer_interval,
        d1_timer_interval,
        d2_timer_interval,
        key_command_map,
    ):
        self.keyboard_active = keyboard_active
        self.cross_cmd_active = cross_cmd_active
        self.key_command_map = key_command_map
        self.default_timer_interval = default_timer_interval
        self.d1_timer_interval = d1_timer_interval
        self.d2_timer_interval = d2_timer_interval

        self.main_command_processor = KeyCommandManager()

        # Processors for directional commands (walk and face)
        self.d1_command_processor = KeyCommandManager()  # walk
        self.d2_command_processor = KeyCommandManager()  # face

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # Toggle keyboard events if encountering a cross hands command
    def check_cross_command(self, command):
        if self.cross_cmd_active and command == "cross":
            self.keyboard_active = not self.keyboard_active
            self.main_command_processor._release_active_key()
            self.d1_command_processor._release_active_key()
            self.d2_command_processor._release_active_key()

    # Add command to the appropriate processor
    def add_command(self, command):
        self.check_cross_command(command)

        if "walk" in command or "d1" in command:
            self.d1_command_processor.record_key_command(
                command,
                self.keyboard_active,
                self.key_command_map,
                self.d1_timer_interval,
            )
        elif "face" in command or "d2" in command:
            self.d2_command_processor.record_key_command(
                command,
                self.keyboard_active,
                self.key_command_map,
                self.d2_timer_interval,
            )
        else:
            self.main_command_processor.record_key_command(
                command,
                self.keyboard_active,
                self.key_command_map,
                self.default_timer_interval,
            )

    def __str__(self):
        return f"""
D1 ({len(self.d1_command_processor._key_command_log)}): {self.d1_command_processor}

D2 ({len(self.d2_command_processor._key_command_log)}): {self.d2_command_processor}

Events ({len(self.main_command_processor._key_command_log)}): {self.main_command_processor}"""
