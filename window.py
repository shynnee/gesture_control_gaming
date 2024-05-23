import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QCheckBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QSlider,
    QPushButton,
)
from pynput.keyboard import Key
from Cv2Thread import ThreadCV2 as ImageProcessorThread
from body.image_config import IMG_HEIGHT as IMG_H, IMG_WIDTH as IMG_W

# Configuration for pose detection
pose_config = dict(
    min_detection_confidence=0,
    min_tracking_confidence=0,
    model_complexity=2,
    enable_segmentation=True,
)

activity_mode = "Action"

# Configuration for body processing
processing_config = dict(
    draw_angles=False,  # Show calculated angles on camera
    show_coords=False,  # Show body coordinates
)

control_mapping = dict(
    name="teamkamenrider",
    mappings=dict(
        cross="",
        right_swing=Key.space,
        right_swing_hold="w",
        walk="s",
        squat=Key.enter,
        face_tilt_left="a",
        face_tilt_right="d",
    )
)

event_settings = dict(
    keyboard_active=False,  # toggle keyboard events
    cross_cmd_active=True,  # toggle cross command (used for toggling keyboard events)
    default_timer_interval=0.3,  # key pressed interval
    d1_timer_interval=1.0,  # key pressed interval for walking commands
    d2_timer_interval=0.1,  # key pressed interval for face tilt commands
    key_command_map=control_mapping["mappings"],
)

configurations = [
    dict(
        name="Min detection confidence",
        key="min_detection_confidence",
        type="pose",
        input="slider_percentage",
        min=0,
        max=100,
        value=pose_config["min_detection_confidence"] * 100,
        hidden=True,
    ),
    dict(
        name="Min detection confidence",
        key="min_tracking_confidence",
        type="pose",
        input="slider_percentage",
        min=0,
        max=100,
        value=pose_config["min_tracking_confidence"] * 100,
        hidden=True,
    ),
    dict(
        name="Model complexity",
        key="model_complexity",
        type="pose",
        input="slider",
        min=0,
        max=2,
        value=pose_config["model_complexity"],
        hidden=True,
    ),
    dict(
        name="Show segmentation", key="enable_segmentation", type="pose", input="checkbox"
    ),
    dict(name="Show angles", key="draw_angles", type="body", input="checkbox"),
    dict(name="Show body coords", key="show_coords", type="body", input="checkbox"),
    dict(
        name="Active keyboard", key="keyboard_active", type="events", input="checkbox"
    ),
    dict(
        name="Use cross to toggle keyboard",
        key="cross_cmd_active",
        type="events",
        input="checkbox",
    ),
]


class PoseDetectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Detection")
        self.setGeometry(100, 100, 900, 650)

        self.display_label = QLabel(self)
        self.display_label.setFixedSize(IMG_W, IMG_H)

        config_layout = QVBoxLayout()

        self.restart_btn = QPushButton(text="Restart Camera")
        self.restart_btn.clicked.connect(self.restart_camera)

        self.initialize_camera_thread()

        for config in configurations:
            if "hidden" in config and config["hidden"]:
                continue
            input_type = config["input"]
            if input_type == "checkbox":
                self.add_checkbox(config, config_layout)
            elif "slider" in input_type:
                self.add_slider(config, config_layout)

        self.add_control_modes_label(config_layout)
        self.add_control_options_label(config_layout)

        self.status_label = QLabel(self)
        self.status_label.setMinimumSize(550, 500)
        self.status_label.setMaximumSize(550, 1000)
        self.status_label.setWordWrap(True)
        config_layout.addWidget(self.status_label)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.display_label)
        main_layout.addLayout(config_layout)

        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.camera_thread.start()

    def initialize_camera_thread(self):
        self.camera_thread = ImageProcessorThread(
            self,
            mp_config=pose_config,
            body_config=processing_config,
            events_config=event_settings,
        )
        self.camera_thread.finished.connect(self.close)
        self.camera_thread.emit_frame_update.connect(self.update_image)
        self.camera_thread.emit_state_update.connect(self.update_status)

        self.restart_btn.setDisabled(True)

    def restart_camera(self):
        self.initialize_camera_thread()
        self.camera_thread.start()

    @Slot(QImage)
    def update_image(self, image):
        self.display_label.setPixmap(QPixmap.fromImage(image))

    @Slot(dict)
    def update_status(self, status):
        self.status_label.setText(str(status["body"]))
        self.restart_btn.setDisabled(False)

    def add_slider(self, slider, layout):
        key = slider["key"]
        config_type = slider["type"]
        input_type = slider["input"]

        row = QFormLayout()

        slider_widget = QSlider(Qt.Horizontal)
        slider_widget.setRange(slider["min"], slider["max"])
        slider_widget.setValue(slider["value"])
        slider_widget.setSingleStep(1)
        slider_widget.valueChanged.connect(
            lambda value: self.on_slider_value_changed(key, value, config_type, input_type)
        )
        row.addRow(slider["name"], slider_widget)
        layout.addLayout(row)

    def on_slider_value_changed(self, key, value, config_type, input_type):
        if "percentage" in input_type:
            value /= 100
        if config_type == "pose":
            self.camera_thread.mp_config[key] = value
        elif config_type == "body":
            self.camera_thread.body[key] = value
        elif config_type == "events":
            self.camera_thread.body.events[key] = value

    def add_checkbox(self, checkbox, layout):
        checkbox_widget = QCheckBox(checkbox["name"])
        key = checkbox["key"]
        config_type = checkbox["type"]

        checked = Qt.Unchecked
        if config_type == "pose":
            checked = Qt.Checked if pose_config[key] else Qt.Unchecked
        elif config_type == "body":
            checked = Qt.Checked if processing_config[key] else Qt.Unchecked
        elif config_type == "events":
            checked = Qt.Checked if event_settings[key] else Qt.Unchecked
        checkbox_widget.setCheckState(checked)

        checkbox_widget.stateChanged.connect(
            lambda value: self.on_checkbox_state_changed(key, value, config_type)
        )
        layout.addWidget(checkbox_widget)

    def on_checkbox_state_changed(self, key, value, config_type):
        if config_type == "pose":
            self.camera_thread.mp_config[key] = not not value
        elif config_type == "body":
            self.camera_thread.body[key] = not not value
        elif config_type == "events":
            self.camera_thread.body.EventHandler[key] = not not value

    def add_control_options_label(self, layout):
        control_row = QFormLayout()

        control_label = QLabel(control_mapping["name"])
        control_label.setMaximumSize(150, 100)

        control_row.addRow("Control", control_label)
        layout.addLayout(control_row)

    def add_control_modes_label(self, layout):
        mode_row = QFormLayout()

        mode_label = QLabel(activity_mode)
        mode_label.setMaximumSize(150, 100)

        mode_row.addRow("Mode", mode_label)
        layout.addLayout(mode_row)


if __name__ == "__main__":
    app = QApplication()
    window = PoseDetectionWindow()
    window.show()
    sys.exit(app.exec())
