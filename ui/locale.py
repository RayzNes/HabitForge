# ui/locale.py

from typing import Dict, Any

# Словари с переводами
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ru": {
        # Общие
        "app_name": "HabitForge — Трекер Привычек",
        "save": "Сохранить",
        "cancel": "Отмена",
        "delete": "Удалить",
        "edit": "Редактировать",
        "add": "Добавить",
        "close": "Закрыть",
        "yes": "Да",
        "no": "Нет",

        # Навигация
        "nav_dashboard": "Dashboard",
        "nav_habits": "Привычки",
        "nav_pomodoro": "Pomodoro",
        "nav_stats": "Статистика",
        "nav_settings": "Настройки",

        # Dashboard
        "good_morning": "Доброе утро, Искатель!",
        "good_afternoon": "Добрый день, Искатель!",
        "good_evening": "Добрый вечер, Искатель!",
        "level": "Уровень",
        "today_habits": "Привычки на сегодня",

        # Привычки
        "add_habit": "+ Добавить привычку",
        "mark_complete": "Отметить выполненной",
        "habit_name": "Название",
        "habit_icon": "Иконка",
        "habit_color": "Цвет",
        "habit_category": "Категория",
        "habit_frequency": "Периодичность",
        "daily": "Ежедневно",
        "weekly": "Еженедельно",

        # Статистика
        "stats_title": "📊 Статистика привычек",
        "current_streak": "🔥 Текущая серия",
        "best_streak": "🏆 Лучшая серия",
        "category_stats": "📈 Выполнение по категориям",
        "weekly_progress": "📅 Прогресс за неделю",
        "activity_heatmap": "📆 Календарь активности",
        "refresh_stats": "🔄 Обновить статистику",

        # Настройки
        "settings_title": "⚙️ Настройки приложения",
        "appearance": "🎨 Внешний вид",
        "theme": "Тема оформления",
        "theme_dark": "🌙 Тёмная",
        "theme_light": "☀️ Светлая",
        "theme_ocean": "🌊 Океан",
        "theme_forest": "🌲 Лесная",
        "theme_sunset": "🌅 Закат",
        "language": "Язык интерфейса",
        "restart_hint": "ℹ️ Изменение темы и языка применяется после перезапуска приложения",
        "save_settings": "💾 Сохранить настройки",
        "restart_app": "🔄 Перезапустить приложение",

        # Напоминания
        "reminders_title": "🔔 Настройки напоминаний",
        "reminders_enabled": "Включить напоминания",
        "reminder_time": "Время ежедневного напоминания",
        "notification_sound": "Включить звук уведомлений",
        "test_notification": "🔔 Тестовое уведомление",
        "active_habits": "Активные привычки для напоминаний",

        # Уведомления
        "notification_habit_reminder": "⏰ Напоминание о привычках",
        "notification_daily_title": "📊 Итоги дня в HabitForge",
        "notification_perfect_title": "🎉 Отличная работа!",
        "notification_test_title": "HabitForge - Напоминания работают!",

        # Сообщения
        "msg_settings_saved": "Настройки сохранены!",
        "msg_restart_confirm": "Для применения изменений необходимо перезапустить приложение. Перезапустить сейчас?",
        "msg_habit_completed": "Отличная работа! +10 XP",
        "msg_already_completed": "Вы уже выполнили эту привычку сегодня!",
        "msg_select_habit": "Пожалуйста, выберите привычку",
        "msg_name_required": "Название обязательно",
    },
    "en": {
        # General
        "app_name": "HabitForge — Habit Tracker",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "close": "Close",
        "yes": "Yes",
        "no": "No",

        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_habits": "Habits",
        "nav_pomodoro": "Pomodoro",
        "nav_stats": "Statistics",
        "nav_settings": "Settings",

        # Dashboard
        "good_morning": "Good morning, Adventurer!",
        "good_afternoon": "Good afternoon, Adventurer!",
        "good_evening": "Good evening, Adventurer!",
        "level": "Level",
        "today_habits": "Today's Habits",

        # Habits
        "add_habit": "+ Add New Habit",
        "mark_complete": "Mark Complete",
        "habit_name": "Name",
        "habit_icon": "Icon",
        "habit_color": "Color",
        "habit_category": "Category",
        "habit_frequency": "Frequency",
        "daily": "Daily",
        "weekly": "Weekly",

        # Statistics
        "stats_title": "📊 Habit Statistics",
        "current_streak": "🔥 Current Streak",
        "best_streak": "🏆 Best Streak",
        "category_stats": "📈 Completion by Category",
        "weekly_progress": "📅 Weekly Progress",
        "activity_heatmap": "📆 Activity Heatmap",
        "refresh_stats": "🔄 Refresh Statistics",

        # Settings
        "settings_title": "⚙️ Application Settings",
        "appearance": "🎨 Appearance",
        "theme": "Theme",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "theme_ocean": "🌊 Ocean",
        "theme_forest": "🌲 Forest",
        "theme_sunset": "🌅 Sunset",
        "language": "Interface Language",
        "restart_hint": "ℹ️ Theme and language changes apply after restart",
        "save_settings": "💾 Save Settings",
        "restart_app": "🔄 Restart Application",

        # Reminders
        "reminders_title": "🔔 Reminder Settings",
        "reminders_enabled": "Enable Reminders",
        "reminder_time": "Daily Reminder Time",
        "notification_sound": "Enable Notification Sound",
        "test_notification": "🔔 Test Notification",
        "active_habits": "Active Habits for Reminders",

        # Notifications
        "notification_habit_reminder": "⏰ Habit Reminder",
        "notification_daily_title": "📊 HabitForge Daily Summary",
        "notification_perfect_title": "🎉 Great job!",
        "notification_test_title": "HabitForge - Reminders are working!",

        # Messages
        "msg_settings_saved": "Settings saved!",
        "msg_restart_confirm": "Changes will take effect after restart. Restart now?",
        "msg_habit_completed": "Great job! +10 XP",
        "msg_already_completed": "You've already completed this habit today!",
        "msg_select_habit": "Please select a habit",
        "msg_name_required": "Name is required",
    },
}


class Translator:
    """Класс для управления переводами"""

    _instance = None
    _current_language = "ru"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_language(self, language_code: str):
        """Установить текущий язык"""
        if language_code in TRANSLATIONS:
            self._current_language = language_code
        else:
            self._current_language = "ru"

    def get_language(self) -> str:
        """Получить текущий язык"""
        return self._current_language

    def tr(self, key: str) -> str:
        """Получить перевод по ключу"""
        return TRANSLATIONS.get(self._current_language, TRANSLATIONS["ru"]).get(key, key)


# Глобальный экземпляр переводчика
translator = Translator()


def tr(key: str) -> str:
    """Удобная функция для перевода"""
    return translator.tr(key)