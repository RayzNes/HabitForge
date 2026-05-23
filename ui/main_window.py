# ui/main_window.py (обновленная версия с настройками)

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from database import get_db
from ui.dashboard_widget import DashboardWidget
from ui.habit_list_widget import HabitListWidget
from ui.pomodoro_widget import PomodoroWidget
from ui.stats_widget import StatsWidget
from ui.reminder_settings_widget import ReminderSettingsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HabitForge — Трекер Привычек")
        self.resize(1400, 900)

        # Create database session
        self.session = get_db()
        self.reminder_service = None

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stacked Widget для переключения экранов
        self.stack = QStackedWidget()

        # Создаём виджеты
        self.dashboard = DashboardWidget(self.session)
        self.habits_page = HabitListWidget(self.session, self)
        self.pomodoro = PomodoroWidget()
        self.stats = StatsWidget(self.session)
        self.reminder_settings = None  # Будет создан после установки сервиса

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.habits_page)
        self.stack.addWidget(self.pomodoro)
        self.stack.addWidget(self.stats)

        layout.addWidget(self.stack)

        # Sidebar
        self.setup_sidebar()

    def set_reminder_service(self, reminder_service):
        """Установить сервис напоминаний и создать виджет настроек"""
        self.reminder_service = reminder_service
        self.reminder_settings = ReminderSettingsWidget(self.session, self.reminder_service, self)
        self.stack.addWidget(self.reminder_settings)

        # Обновляем меню
        self.update_menu()

    def setup_sidebar(self):
        """Базовое меню без настроек напоминаний"""
        menubar = self.menuBar()
        nav_menu = menubar.addMenu("Навигация")

        nav_menu.addAction("Dashboard", lambda: self.stack.setCurrentWidget(self.dashboard))
        nav_menu.addAction("Привычки", lambda: self.stack.setCurrentWidget(self.habits_page))
        nav_menu.addAction("Pomodoro", lambda: self.stack.setCurrentWidget(self.pomodoro))
        nav_menu.addAction("Статистика", lambda: self.stack.setCurrentWidget(self.stats))

        # Add menu for creating new habits
        habit_menu = menubar.addMenu("Привычки")
        habit_menu.addAction("Добавить привычку", self.add_new_habit)

    def update_menu(self):
        """Обновить меню с настройками напоминаний"""
        menubar = self.menuBar()

        # Добавляем пункт "Настройки" если его ещё нет
        settings_menu = menubar.addMenu("⚙ Настройки")
        settings_menu.addAction("🔔 Напоминания", lambda: self.stack.setCurrentWidget(self.reminder_settings))

    def add_new_habit(self):
        from ui.dialogs.habit_dialog import HabitDialog
        dialog = HabitDialog(self.session, parent=self)
        if dialog.exec():
            self.habits_page.load_habits()
            self.dashboard.refresh()
            self.stats.refresh()
            if self.reminder_settings:
                self.reminder_settings.update_habits_info()

    def closeEvent(self, event):
        if self.reminder_service:
            self.reminder_service.stop()
        self.session.close()
        event.accept()