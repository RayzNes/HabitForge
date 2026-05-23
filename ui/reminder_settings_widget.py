# ui/reminder_settings_widget.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QSpinBox, QPushButton, QGroupBox,
                               QMessageBox)
from PySide6.QtCore import Qt
from models.user_settings import UserSettings
from utils.reminder import ReminderService


class ReminderSettingsWidget(QWidget):
    """Виджет настроек напоминаний"""

    def __init__(self, session, reminder_service: ReminderService, parent=None):
        super().__init__(parent)
        self.session = session
        self.reminder_service = reminder_service
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        header = QLabel("🔔 Настройки напоминаний")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Группа основных настроек
        main_group = QGroupBox("Основные настройки")
        main_layout = QVBoxLayout(main_group)

        # Включение/выключение напоминаний
        self.enable_checkbox = QCheckBox("Включить напоминания")
        self.enable_checkbox.toggled.connect(self.on_reminders_toggled)
        main_layout.addWidget(self.enable_checkbox)

        # Время напоминания
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Время ежедневного напоминания:"))

        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setSuffix(" ч")
        time_layout.addWidget(self.hour_spin)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setSuffix(" мин")
        time_layout.addWidget(self.minute_spin)

        time_layout.addStretch()
        main_layout.addLayout(time_layout)

        # Звук уведомлений
        self.sound_checkbox = QCheckBox("Включить звук уведомлений")
        main_layout.addWidget(self.sound_checkbox)

        layout.addWidget(main_group)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)

        self.test_btn = QPushButton("🔔 Тестовое уведомление")
        self.test_btn.clicked.connect(self.test_notification)
        buttons_layout.addWidget(self.test_btn)

        layout.addLayout(buttons_layout)

        # Информация о статусе
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #8ab4f7; padding: 10px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Список привычек для напоминаний
        habits_group = QGroupBox("Активные привычки для напоминаний")
        habits_layout = QVBoxLayout(habits_group)

        self.habits_info = QLabel("Загружаем список привычек...")
        self.habits_info.setWordWrap(True)
        habits_layout.addWidget(self.habits_info)

        layout.addWidget(habits_group)

        layout.addStretch()

    def load_settings(self):
        """Загрузить настройки из БД"""
        settings = self.session.query(UserSettings).first()

        if settings:
            self.enable_checkbox.setChecked(settings.reminders_enabled)
            self.hour_spin.setValue(settings.reminder_hour)
            self.minute_spin.setValue(settings.reminder_minute)
            self.sound_checkbox.setChecked(settings.notification_sound)

        # Обновляем статус сервиса
        if self.reminder_service:
            self.reminder_service.reminders_enabled = self.enable_checkbox.isChecked()
            self.reminder_service.set_reminder_time(self.hour_spin.value(), self.minute_spin.value())

        self.update_habits_info()
        self.update_status()

    def update_habits_info(self):
        """Обновить информацию о привычках"""
        from models.habit import Habit, Frequency

        habits = self.session.query(Habit).all()

        if habits:
            info = "Привычки, по которым будут приходить напоминания:\n\n"
            for habit in habits:
                freq_str = "ежедневно" if habit.frequency == Frequency.DAILY else "еженедельно"
                info += f"  • {habit.icon} {habit.name} ({freq_str})\n"
        else:
            info = "Нет добавленных привычек. Добавьте привычки, чтобы получать напоминания."

        self.habits_info.setText(info)

    def update_status(self):
        """Обновить статус напоминаний"""
        if self.enable_checkbox.isChecked():
            time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}"
            self.status_label.setText(
                f"✅ Напоминания включены. Ежедневное напоминание в {time_str}\n"
                f"Проверка привычек выполняется каждые {self.reminder_service.check_interval} секунд."
            )
        else:
            self.status_label.setText("⏸ Напоминания выключены")

    def on_reminders_toggled(self, enabled):
        """Обработчик переключения напоминаний"""
        if self.reminder_service:
            self.reminder_service.toggle_reminders(enabled)
        self.update_status()

    def save_settings(self):
        """Сохранить настройки в БД"""
        settings = self.session.query(UserSettings).first()

        if not settings:
            settings = UserSettings()
            self.session.add(settings)

        settings.reminders_enabled = self.enable_checkbox.isChecked()
        settings.reminder_hour = self.hour_spin.value()
        settings.reminder_minute = self.minute_spin.value()
        settings.notification_sound = self.sound_checkbox.isChecked()

        self.session.commit()

        # Обновляем сервис
        if self.reminder_service:
            self.reminder_service.reminders_enabled = self.enable_checkbox.isChecked()
            self.reminder_service.set_reminder_time(self.hour_spin.value(), self.minute_spin.value())

        self.update_status()

        QMessageBox.information(self, "Успех", "Настройки сохранены!")

    def test_notification(self):
        """Отправить тестовое уведомление"""
        if self.reminder_service:
            success = self.reminder_service.send_test_notification()
            if success:
                QMessageBox.information(self, "Тест", "Тестовое уведомление отправлено!")
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Не удалось отправить уведомление.\n"
                                    "Убедитесь, что системные уведомления разрешены для этого приложения.")