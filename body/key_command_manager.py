from datetime import datetime
from pynput.keyboard import Controller
from threading import Timer


class KeyCommandManager:
    def __init__(self):
        self._keyboard_controller = Controller()
        self._key_command_log = []
        self._active_key = None
        self._key_release_timer = None

    def _release_active_key(self):
        if self._active_key:
            active_key_code = self._active_key["key"]
            self._keyboard_controller.release(active_key_code)
            self._active_key = None

    def _trim_command_log(self):
        if len(self._key_command_log) > 900:
            self._key_command_log = self._key_command_log[-10:]

    def record_key_command(
        self,
        command,
        is_keyboard_enabled: bool,
        key_mapping: dict,
        key_hold_duration: float,
    ):
        self._trim_command_log()

        timestamp = datetime.now()
        self._key_command_log.insert(0, {"command": command, "timestamp": timestamp})

        if is_keyboard_enabled:
            if command in key_mapping:
                mapped_key = key_mapping[command]
                previous_key_code = None
                if self._active_key:
                    previous_key_code = self._active_key["key"]

                if self._key_release_timer and self._key_release_timer.is_alive():
                    self._key_release_timer.cancel()

                if previous_key_code != mapped_key:
                    self._release_active_key()
                    if mapped_key:
                        self._keyboard_controller.press(mapped_key)

                if mapped_key:
                    self._key_release_timer = Timer(
                        key_hold_duration,
                        self._release_active_key,
                    )
                    self._key_release_timer.start()

                    self._active_key = {"key": mapped_key, "timestamp": timestamp}

    def __str__(self):
        commands_list = [entry["command"] for entry in self._key_command_log]
        if not commands_list:
            return ""
        return commands_list[0] + "\n" + ", ".join(commands_list[1:20])
