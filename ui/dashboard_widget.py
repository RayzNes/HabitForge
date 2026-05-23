from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
from models.habit import Habit
from models.user_progress import UserProgress
from utils.streak import calculate_current_streak


class DashboardWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        self.header = QLabel("Good morning, Adventurer!")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        layout.addWidget(self.header)

        # Progress row
        progress_layout = QHBoxLayout()

        self.xp_bar = QProgressBar()
        self.xp_bar.setMaximum(100)
        progress_layout.addWidget(QLabel("Level"))
        progress_layout.addWidget(self.xp_bar)

        layout.addLayout(progress_layout)

        # Today's habits
        self.today_label = QLabel("Today's Habits")
        layout.addWidget(self.today_label)

        # Placeholder for chart
        self.figure = plt.figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.refresh()

    def refresh(self):
        # Update XP
        progress = self.session.query(UserProgress).first()
        if progress:
            next_level_xp = 100 * (1.5 ** (progress.level - 1))
            self.xp_bar.setValue(int((progress.xp / next_level_xp) * 100))
            self.xp_bar.setFormat(f"Level {progress.level} - {int(progress.xp)}/{int(next_level_xp)} XP")
        else:
            self.xp_bar.setValue(0)
            self.xp_bar.setFormat("Level 1 - 0/100 XP")

        # Simple activity plot
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        values = [3, 5, 4, 6, 2, 4, 5]
        ax.bar(days, values, color='#4CAF50')
        ax.set_title('Weekly Activity')
        ax.set_ylabel('Completions')
        ax.set_facecolor('#1E1E1E')
        self.figure.set_facecolor('#1E1E1E')
        ax.tick_params(colors='white')
        ax.title.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        self.canvas.draw()