from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                               QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from models.habit import Habit
from models.completion import HabitCompletion
from models.user_progress import UserProgress
from datetime import datetime
from utils.streak import calculate_current_streak


class HabitListWidget(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add button for new habit
        add_btn = QPushButton("+ Add New Habit")
        add_btn.clicked.connect(self.add_new_habit)
        layout.addWidget(add_btn)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        complete_btn = QPushButton("Mark Complete")
        complete_btn.clicked.connect(self.mark_complete)
        btn_layout.addWidget(complete_btn)
        layout.addLayout(btn_layout)

    def add_new_habit(self):
        from ui.dialogs.habit_dialog import HabitDialog
        dialog = HabitDialog(self.session, parent=self)
        if dialog.exec():
            self.load_habits()
            if self.parent_window and hasattr(self.parent_window, 'dashboard'):
                self.parent_window.dashboard.refresh()

    def load_habits(self):
        self.list_widget.clear()
        habits = self.session.query(Habit).all()

        for habit in habits:
            item = QListWidgetItem()
            streak = calculate_current_streak(self.session, habit.id)
            text = f"{habit.icon} {habit.name} | Streak: {streak} | {habit.category}"
            item.setText(text)
            item.setData(Qt.UserRole, habit.id)
            self.list_widget.addItem(item)

    def mark_complete(self):
        current = self.list_widget.currentItem()
        if not current:
            QMessageBox.information(self, "Info", "Please select a habit to mark as complete")
            return

        habit_id = current.data(Qt.UserRole)
        habit = self.session.query(Habit).get(habit_id)

        # Check if already completed today
        today = datetime.utcnow().date()
        existing = self.session.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.date >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).first()

        if existing:
            QMessageBox.warning(self, "Warning", f"You've already completed '{habit.name}' today!")
            return

        completion = HabitCompletion(habit_id=habit_id, note="Completed via app")
        self.session.add(completion)

        # Add XP
        progress = self.session.query(UserProgress).first()
        if progress:
            progress.add_xp(10)
        else:
            # Create progress if it doesn't exist
            progress = UserProgress()
            progress.add_xp(10)
            self.session.add(progress)

        self.session.commit()
        self.load_habits()
        if self.parent_window and hasattr(self.parent_window, 'dashboard'):
            self.parent_window.dashboard.refresh()

        QMessageBox.information(self, "Success", f"Great job completing '{habit.name}'! +10 XP")