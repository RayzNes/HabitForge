# main.py (обновленная версия)

import sys
import logging
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt

from database import init_db
from ui.main_window import MainWindow
from data.seed import seed_demo_data
from utils.reminder import ReminderService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def apply_dark_theme(app):
    """Простая, но надёжная тёмная тема без внешних зависимостей"""
    app.setStyle(QStyleFactory.create("Fusion"))

    dark_palette = {
        "background": "#1E1E1E",
        "window": "#2D2D2D",
        "windowText": "#FFFFFF",
        "base": "#383838",
        "alternateBase": "#2D2D2D",
        "toolTipBase": "#2D2D2D",
        "toolTipText": "#FFFFFF",
        "text": "#FFFFFF",
        "button": "#2D2D2D",
        "buttonText": "#FFFFFF",
        "link": "#8ab4f7",
        "highlight": "#4A90E2",
        "highlightedText": "#FFFFFF",
    }

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, dark_palette["window"])
    palette.setColor(QPalette.ColorRole.WindowText, dark_palette["windowText"])
    palette.setColor(QPalette.ColorRole.Base, dark_palette["base"])
    palette.setColor(QPalette.ColorRole.AlternateBase, dark_palette["alternateBase"])
    palette.setColor(QPalette.ColorRole.ToolTipBase, dark_palette["toolTipBase"])
    palette.setColor(QPalette.ColorRole.ToolTipText, dark_palette["toolTipText"])
    palette.setColor(QPalette.ColorRole.Text, dark_palette["text"])
    palette.setColor(QPalette.ColorRole.Button, dark_palette["button"])
    palette.setColor(QPalette.ColorRole.ButtonText, dark_palette["buttonText"])
    palette.setColor(QPalette.ColorRole.Link, dark_palette["link"])
    palette.setColor(QPalette.ColorRole.Highlight, dark_palette["highlight"])
    palette.setColor(QPalette.ColorRole.HighlightedText, dark_palette["highlightedText"])

    app.setPalette(palette)
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #2D2D2D;
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #3D3D3D;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #383838;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
        }
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """)


def main():
    init_db()
    seed_demo_data()

    app = QApplication(sys.argv)
    apply_dark_theme(app)

    # Создаём окно (оно создаст сессию)
    window = MainWindow()

    # Создаём сервис напоминаний с той же сессией
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