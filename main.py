# main.py (обновленная версия с загрузкой сохраненной темы)

import sys
import logging
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QSettings

from database import init_db
from ui.main_window import MainWindow
from data.seed import seed_demo_data
from utils.reminder import ReminderService
from ui.settings_widget import SettingsWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def apply_theme_from_settings(app):
    """Применить тему из сохранённых настроек"""
    from models.user_settings import UserSettings
    from database import SessionLocal

    app.setStyle(QStyleFactory.create("Fusion"))

    # Пытаемся загрузить тему из БД
    try:
        db = SessionLocal()
        settings = db.query(UserSettings).first()
        theme_key = settings.theme if settings else "dark"
        db.close()
    except Exception:
        # Если БД ещё не инициализирована или ошибка, пробуем QSettings
        qt_settings = QSettings("HabitForge", "Settings")
        theme_key = qt_settings.value("theme", "dark")

    # Применяем тему
    themes = {
        "dark": {
            "window": "#2D2D2D", "base": "#383838", "text": "#FFFFFF",
            "button": "#2D2D2D", "highlight": "#4A90E2",
        },
        "light": {
            "window": "#F0F0F0", "base": "#FFFFFF", "text": "#333333",
            "button": "#E0E0E0", "highlight": "#2196F3",
        },
        "ocean": {
            "window": "#1a3a4f", "base": "#1e4d6b", "text": "#e0f7fa",
            "button": "#1e4d6b", "highlight": "#00bcd4",
        },
        "forest": {
            "window": "#1a3f2a", "base": "#2e5c3e", "text": "#c8e6c9",
            "button": "#2e5c3e", "highlight": "#4caf50",
        },
        "sunset": {
            "window": "#4a2a1a", "base": "#6b3e2a", "text": "#ffe0b2",
            "button": "#6b3e2a", "highlight": "#ff9800",
        },
    }

    theme = themes.get(theme_key, themes["dark"])
    palette = app.palette()

    palette.setColor(QPalette.ColorRole.Window, QColor(theme["window"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme["base"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["window"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme["button"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["highlight"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)

    # Стили
    extra_style = f"""
        QMainWindow, QWidget {{
            background-color: {theme["window"]};
            color: {theme["text"]};
        }}
        QPushButton {{
            background-color: {theme["button"]};
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background-color: {theme["highlight"]};
        }}
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {theme["base"]};
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
        }}
        QGroupBox {{
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        QProgressBar {{
            border: 1px solid #555;
            border-radius: 5px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {theme["highlight"]};
            border-radius: 5px;
        }}
        QListWidget {{
            background-color: {theme["base"]};
            border: 1px solid #555;
            border-radius: 5px;
        }}
        QListWidget::item {{
            padding: 8px;
        }}
        QListWidget::item:selected {{
            background-color: {theme["highlight"]};
        }}
        QMenuBar {{
            background-color: {theme["window"]};
            color: {theme["text"]};
        }}
        QMenuBar::item:selected {{
            background-color: {theme["highlight"]};
        }}
        QMenu {{
            background-color: {theme["window"]};
            color: {theme["text"]};
            border: 1px solid #555;
        }}
        QMenu::item:selected {{
            background-color: {theme["highlight"]};
        }}
    """
    app.setStyleSheet(extra_style)

    return theme_key


def main():
    # Инициализация БД (создаёт таблицы, включая user_settings)
    init_db()
    seed_demo_data()

    app = QApplication(sys.argv)

    # Применяем сохранённую тему
    current_theme = apply_theme_from_settings(app)
    logging.info(f"Applied theme: {current_theme}")

    # Создаём окно (оно создаст сессию)
    window = MainWindow()

    # Создаём сервис напоминаний
    reminder_service = ReminderService(window.session)
    reminder_service.start()

    # Передаём сервис в окно
    window.set_reminder_service(reminder_service)

    window.showMaximized()

    # Останавливаем сервис при закрытии
    def on_close():
        reminder_service.stop()

    app.aboutToQuit.connect(on_close)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()