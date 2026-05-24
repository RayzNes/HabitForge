# ui/dialogs/habit_dialog.py (исправленная версия)

import re
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QPushButton, QColorDialog, QMessageBox, QHBoxLayout,
                               QCheckBox, QLabel, QWidget)
from PySide6.QtCore import Qt
from models.habit import Habit, Frequency


class HabitDialog(QDialog):
    def __init__(self, session, habit=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.habit = habit
        self.setWindowTitle("Новая привычка" if not habit else "Редактирование привычки")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        # Название с валидацией
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(100)
        self.name_edit.setPlaceholderText("Например: Пить воду, Читать книги...")
        self.name_edit.textChanged.connect(self.validate_name)
        form.addRow("Название:*", self.name_edit)

        self.name_error = QLabel()
        self.name_error.setStyleSheet("color: #f44336; font-size: 11px;")
        self.name_error.setVisible(False)
        form.addRow("", self.name_error)

        # Иконка
        self.icon_edit = QLineEdit("✅")
        self.icon_edit.setMaxLength(10)
        self.icon_edit.setPlaceholderText("Emoji или символ")
        form.addRow("Иконка:", self.icon_edit)

        # Цвет
        self.color_btn = QPushButton("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_color)
        self.current_color = "#4CAF50"
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet(f"background-color: {self.current_color}; border-radius: 5px;")

        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        form.addRow("Цвет:", color_layout)

        # Категория
        self.category_edit = QComboBox()
        categories = ["Здоровье", "Развитие", "Ментальное здоровье", "Продуктивность", "Общее"]
        self.category_edit.addItems(categories)
        form.addRow("Категория:", self.category_edit)

        # Периодичность
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["Ежедневно", "Еженедельно"])
        self.freq_combo.currentTextChanged.connect(self.on_frequency_changed)
        form.addRow("Периодичность:", self.freq_combo)

        # Дни недели (для еженедельных)
        self.weekdays_widget = QWidget()
        weekdays_layout = QHBoxLayout(self.weekdays_widget)
        weekdays_layout.setContentsMargins(0, 0, 0, 0)

        self.weekday_checkboxes = {}
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(weekdays, 1):
            cb = QCheckBox(day)
            cb.setChecked(i <= 5)  # По умолчанию будни
            self.weekday_checkboxes[i] = cb
            weekdays_layout.addWidget(cb)

        weekdays_layout.addStretch()
        self.weekdays_widget.setVisible(False)
        form.addRow("Дни недели:", self.weekdays_widget)

        # Описание (опционально)
        self.description_edit = QLineEdit()
        self.description_edit.setMaxLength(200)
        self.description_edit.setPlaceholderText("Краткое описание привычки (опционально)")
        form.addRow("Описание:", self.description_edit)

        layout.addLayout(form)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_habit)
        save_btn.setStyleSheet("background-color: #4CAF50;")

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Загрузка данных для редактирования
        if self.habit:
            self.load_habit_data()

    def load_habit_data(self):
        """Загрузить данные привычки для редактирования"""
        self.name_edit.setText(self.habit.name)
        self.icon_edit.setText(self.habit.icon)
        self.current_color = self.habit.color
        self.color_preview.setStyleSheet(f"background-color: {self.current_color}; border-radius: 5px;")
        self.category_edit.setCurrentText(self.habit.category)

        if self.habit.frequency == Frequency.DAILY:
            self.freq_combo.setCurrentText("Ежедневно")
        else:
            self.freq_combo.setCurrentText("Еженедельно")
            if self.habit.days_of_week:
                days = [int(d.strip()) for d in self.habit.days_of_week.split(',') if d.strip()]
                for day in days:
                    if day in self.weekday_checkboxes:
                        self.weekday_checkboxes[day].setChecked(True)

    def on_frequency_changed(self, text):
        """Обработчик изменения периодичности"""
        self.weekdays_widget.setVisible(text == "Еженедельно")

    def choose_color(self):
        """Выбор цвета"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.current_color}; border-radius: 5px;")

    def validate_name(self):
        """Валидация названия"""
        name = self.name_edit.text().strip()

        if not name:
            self.name_error.setText("Название обязательно для заполнения")
            self.name_error.setVisible(True)
            return False

        if len(name) < 2:
            self.name_error.setText("Название должно содержать минимум 2 символа")
            self.name_error.setVisible(True)
            return False

        if len(name) > 100:
            self.name_error.setText("Название не должно превышать 100 символов")
            self.name_error.setVisible(True)
            return False

        # Проверка на дубликаты (при создании новой привычки)
        if not self.habit:
            existing = self.session.query(Habit).filter(
                Habit.name == name
            ).first()
            if existing:
                self.name_error.setText("Привычка с таким названием уже существует")
                self.name_error.setVisible(True)
                return False

        self.name_error.setVisible(False)
        return True

    def validate_icon(self):
        """Валидация иконки"""
        icon = self.icon_edit.text().strip()

        if len(icon) > 10:
            QMessageBox.warning(self, "Ошибка", "Иконка слишком длинная (максимум 10 символов)")
            return False

        return True

    def get_selected_days(self):
        """Получить выбранные дни недели"""
        if self.freq_combo.currentText() == "Ежедневно":
            return ""

        selected_days = [str(day) for day, cb in self.weekday_checkboxes.items() if cb.isChecked()]
        return ",".join(selected_days)

    def save_habit(self):
        """Сохранить привычку с валидацией"""
        # Валидация
        if not self.validate_name():
            return

        if not self.validate_icon():
            return

        name = self.name_edit.text().strip()

        # Для еженедельных привычек проверяем, что выбран хотя бы один день
        if self.freq_combo.currentText() == "Еженедельно":
            selected_days = self.get_selected_days()
            if not selected_days:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Для еженедельной привычки выберите хотя бы один день недели"
                )
                return

        try:
            if not self.habit:
                self.habit = Habit()
                self.session.add(self.habit)

            self.habit.name = name
            self.habit.icon = self.icon_edit.text().strip() or "✅"
            self.habit.color = self.current_color
            self.habit.category = self.category_edit.currentText()

            # Установка периодичности
            if self.freq_combo.currentText() == "Ежедневно":
                self.habit.frequency = Frequency.DAILY
                self.habit.days_of_week = ""
            else:
                self.habit.frequency = Frequency.WEEKLY
                self.habit.days_of_week = self.get_selected_days()

            self.session.commit()
            self.accept()

        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить привычку:\n{str(e)}")