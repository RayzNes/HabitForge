from PySide6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from database import get_db
from ui.dashboard_widget import DashboardWidget
from ui.habit_list_widget import HabitListWidget
from ui.pomodoro_widget import PomodoroWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HabitForge — Трекер Привычек")
        self.resize(1400, 900)

        # Create database session
        self.session = get_db()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Stacked Widget для переключения экранов
        self.stack = QStackedWidget()

        # Создаём виджеты with session parameter
        self.dashboard = DashboardWidget(self.session)
        self.habits_page = HabitListWidget(self.session, self)  # Pass session and self as parent
        self.pomodoro = PomodoroWidget()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.habits_page)
        self.stack.addWidget(self.pomodoro)

        layout.addWidget(self.stack)

        # Sidebar (простая навигация)
        self.setup_sidebar()

    def setup_sidebar(self):
        # Можно улучшить позже, пока простые кнопки в меню
        menubar = self.menuBar()
        nav_menu = menubar.addMenu("Навигация")

        nav_menu.addAction("Dashboard", lambda: self.stack.setCurrentWidget(self.dashboard))
        nav_menu.addAction("Привычки", lambda: self.stack.setCurrentWidget(self.habits_page))
        nav_menu.addAction("Pomodoro", lambda: self.stack.setCurrentWidget(self.pomodoro))

        # Add menu for creating new habits
        habit_menu = menubar.addMenu("Привычки")
        habit_menu.addAction("Добавить привычку", self.add_new_habit)

    def add_new_habit(self):
        from ui.dialogs.habit_dialog import HabitDialog
        dialog = HabitDialog(self.session, parent=self)
        if dialog.exec():
            self.habits_page.load_habits()
            self.dashboard.refresh()

    def closeEvent(self, event):
        self.session.close()
        event.accept()