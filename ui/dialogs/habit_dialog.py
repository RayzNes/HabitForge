from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QPushButton, QColorDialog, QMessageBox, QHBoxLayout)
from PySide6.QtCore import Qt
from models.habit import Habit, Frequency


class HabitDialog(QDialog):
    def __init__(self, session, habit=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.habit = habit
        self.setWindowTitle("New Habit" if not habit else "Edit Habit")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)

        self.icon_edit = QLineEdit("✅")
        form.addRow("Icon:", self.icon_edit)

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.current_color = "#4CAF50"
        form.addRow("Color:", self.color_btn)

        self.category_edit = QComboBox()
        self.category_edit.addItems(["Health", "Learning", "Mindfulness", "Productivity", "General"])
        form.addRow("Category:", self.category_edit)

        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["Daily", "Weekly"])
        form.addRow("Frequency:", self.freq_combo)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_habit)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        if self.habit:
            self.name_edit.setText(self.habit.name)
            self.icon_edit.setText(self.habit.icon)
            self.current_color = self.habit.color
            self.category_edit.setCurrentText(self.habit.category)
            # Set frequency combo based on habit's frequency
            if self.habit.frequency == Frequency.DAILY:
                self.freq_combo.setCurrentText("Daily")
            else:
                self.freq_combo.setCurrentText("Weekly")

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()

    def save_habit(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Name is required")
            return

        if not self.habit:
            self.habit = Habit()
            self.session.add(self.habit)

        self.habit.name = self.name_edit.text()
        self.habit.icon = self.icon_edit.text()
        self.habit.color = self.current_color
        self.habit.category = self.category_edit.currentText()

        # Set frequency using the correct enum
        if self.freq_combo.currentText() == "Daily":
            self.habit.frequency = Frequency.DAILY
        else:
            self.habit.frequency = Frequency.WEEKLY

        self.session.commit()
        self.accept()

    def validate_habit(self):
        if len(self.name_edit.text()) > 100:
            QMessageBox.warning(self, "Error", "Name too long (max 100 chars)")
            return False
        if self.icon_edit.text() and len(self.icon_edit.text()) > 50:
            QMessageBox.warning(self, "Error", "Icon too long")
            return False
        return True