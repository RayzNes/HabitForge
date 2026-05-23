# ui/settings_widget.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QGroupBox, QMessageBox,
                               QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QSettings
from models.user_settings import UserSettings


class SettingsWidget(QWidget):
    """Виджет общих настроек приложения (тема, язык)"""

    # Доступные темы
    THEMES = {
        "dark": {"name": "🌙 Тёмная", "style": "dark"},
        "light": {"name": "☀️ Светлая", "style": "light"},
        "ocean": {"name": "🌊 Океан", "style": "ocean"},
        "forest": {"name": "🌲 Лесная", "style": "forest"},
        "sunset": {"name": "🌅 Закат", "style": "sunset"},
    }

    # Доступные языки
    LANGUAGES = {
        "ru": {"name": "🇷🇺 Русский", "native_name": "Русский"},
        "en": {"name": "🇬🇧 English", "native_name": "English"},
        "es": {"name": "🇪🇸 Español", "native_name": "Español"},
        "fr": {"name": "🇫🇷 Français", "native_name": "Français"},
        "de": {"name": "🇩🇪 Deutsch", "native_name": "Deutsch"},
    }

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.parent_window = parent
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        header = QLabel("⚙️ Настройки приложения")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Группа внешнего вида
        appearance_group = QGroupBox("🎨 Внешний вид")
        appearance_layout = QVBoxLayout(appearance_group)

        # Выбор темы
        theme_label = QLabel("Тема оформления:")
        theme_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        appearance_layout.addWidget(theme_label)

        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        for theme_key, theme_info in self.THEMES.items():
            self.theme_combo.addItem(theme_info["name"], theme_key)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)

        # Предпросмотр темы (опционально)
        self.theme_preview = QLabel()
        self.theme_preview.setFixedHeight(100)
        self.theme_preview.setStyleSheet("border: 1px solid #555; border-radius: 8px; margin-top: 10px;")
        appearance_layout.addWidget(self.theme_preview)

        # Выбор языка
        lang_label = QLabel("Язык интерфейса:")
        lang_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        appearance_layout.addWidget(lang_label)

        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        for lang_code, lang_info in self.LANGUAGES.items():
            self.lang_combo.addItem(f"{lang_info['name']} - {lang_info['native_name']}", lang_code)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        appearance_layout.addLayout(lang_layout)

        layout.addWidget(appearance_group)

        # Информация о применении изменений
        info_label = QLabel("ℹ️ Изменение темы и языка применяется после перезапуска приложения")
        info_label.setStyleSheet("color: #888; padding: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)

        self.restart_btn = QPushButton("🔄 Перезапустить приложение")
        self.restart_btn.clicked.connect(self.restart_app)
        self.restart_btn.setStyleSheet("background-color: #FF5722;")
        buttons_layout.addWidget(self.restart_btn)

        layout.addLayout(buttons_layout)

        # Статус
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.update_theme_preview()

    def load_settings(self):
        """Загрузить настройки из БД"""
        settings = self.session.query(UserSettings).first()

        if settings:
            # Загружаем тему
            theme_index = self.theme_combo.findData(settings.theme)
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)

            # Загружаем язык
            lang_index = self.lang_combo.findData(settings.language)
            if lang_index >= 0:
                self.lang_combo.setCurrentIndex(lang_index)

        self.update_status()

    def update_theme_preview(self):
        """Обновить предпросмотр темы"""
        theme_key = self.theme_combo.currentData()
        preview_style = self.get_preview_style(theme_key)
        self.theme_preview.setStyleSheet(f"""
            border: 1px solid #555;
            border-radius: 8px;
            margin-top: 10px;
            {preview_style}
        """)
        # Добавляем текст предпросмотра
        theme_name = self.theme_combo.currentText()
        self.theme_preview.setText(f"  Предпросмотр: {theme_name}\n  ████████████████████")

    def get_preview_style(self, theme_key):
        """Получить стиль для предпросмотра темы"""
        styles = {
            "dark": "background-color: #1E1E1E; color: #FFFFFF;",
            "light": "background-color: #F5F5F5; color: #333333;",
            "ocean": "background-color: #1a3a4f; color: #e0f7fa;",
            "forest": "background-color: #1a3f2a; color: #c8e6c9;",
            "sunset": "background-color: #4a2a1a; color: #ffe0b2;",
        }
        return styles.get(theme_key, styles["dark"])

    def on_theme_changed(self):
        """Обработчик изменения темы"""
        self.update_theme_preview()
        self.update_status()

    def on_language_changed(self):
        """Обработчик изменения языка"""
        self.update_status()

    def update_status(self):
        """Обновить статусную строку"""
        theme_name = self.theme_combo.currentText()
        lang_code = self.lang_combo.currentData()
        lang_name = self.LANGUAGES.get(lang_code, {}).get("name", "Unknown")
        self.status_label.setText(f"Текущие настройки: {theme_name} тема, {lang_name}")

    def save_settings(self):
        """Сохранить настройки в БД"""
        settings = self.session.query(UserSettings).first()

        if not settings:
            settings = UserSettings()
            self.session.add(settings)

        settings.theme = self.theme_combo.currentData()
        settings.language = self.lang_combo.currentData()

        self.session.commit()

        # Сохраняем в QSettings для быстрого доступа при запуске
        qt_settings = QSettings("HabitForge", "Settings")
        qt_settings.setValue("theme", settings.theme)
        qt_settings.setValue("language", settings.language)

        QMessageBox.information(
            self,
            "Настройки сохранены",
            f"Настройки успешно сохранены!\n\n"
            f"Тема: {self.theme_combo.currentText()}\n"
            f"Язык: {self.lang_combo.currentText()}\n\n"
            f"Изменения вступят в силу после перезапуска приложения."
        )

    def restart_app(self):
        """Перезапустить приложение"""
        reply = QMessageBox.question(
            self,
            "Перезапуск приложения",
            "Для применения изменений необходимо перезапустить приложение.\n"
            "Перезапустить сейчас?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Сохраняем настройки перед перезапуском
            self.save_settings()

            # Перезапуск приложения
            import sys
            import subprocess
            import os

            python = sys.executable
            script = sys.argv[0]
            subprocess.Popen([python, script])
            QApplication.quit()
            sys.exit()

    def apply_theme_to_app(self, app, theme_key):
        """Применить тему к приложению (статический метод)"""
        from PySide6.QtWidgets import QApplication, QStyleFactory
        from PySide6.QtGui import QPalette, QColor

        app.setStyle(QStyleFactory.create("Fusion"))

        themes = {
            "dark": {
                "window": "#2D2D2D",
                "base": "#383838",
                "text": "#FFFFFF",
                "button": "#2D2D2D",
                "highlight": "#4A90E2",
            },
            "light": {
                "window": "#F0F0F0",
                "base": "#FFFFFF",
                "text": "#333333",
                "button": "#E0E0E0",
                "highlight": "#2196F3",
            },
            "ocean": {
                "window": "#1a3a4f",
                "base": "#1e4d6b",
                "text": "#e0f7fa",
                "button": "#1e4d6b",
                "highlight": "#00bcd4",
            },
            "forest": {
                "window": "#1a3f2a",
                "base": "#2e5c3e",
                "text": "#c8e6c9",
                "button": "#2e5c3e",
                "highlight": "#4caf50",
            },
            "sunset": {
                "window": "#4a2a1a",
                "base": "#6b3e2a",
                "text": "#ffe0b2",
                "button": "#6b3e2a",
                "highlight": "#ff9800",
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

        # Дополнительные стили
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
            QProgressBar {{
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {theme["highlight"]};
                border-radius: 5px;
            }}
        """
        app.setStyleSheet(extra_style)


# Импорт для restart_app
from PySide6.QtWidgets import QApplication