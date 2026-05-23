from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QHBoxLayout
from PySide6.QtCore import QTimer, Qt
from datetime import timedelta


class PomodoroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.time_left = 25 * 60  # 25 minutes
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet("font-size: 72px; font-weight: bold;")
        layout.addWidget(self.timer_label)

        self.progress = QProgressBar()
        self.progress.setMaximum(25 * 60)
        layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.toggle_timer)
        btn_layout.addWidget(self.start_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_timer)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("Start")
        else:
            self.timer.start(1000)
            self.start_btn.setText("Pause")
        self.is_running = not self.is_running

    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer.stop()
            self.is_running = False
            self.start_btn.setText("Start")
            self.time_left = 25 * 60
            return

        mins, secs = divmod(self.time_left, 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        self.progress.setValue(25 * 60 - self.time_left)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = 25 * 60
        self.timer_label.setText("25:00")
        self.progress.setValue(0)
        self.start_btn.setText("Start")

