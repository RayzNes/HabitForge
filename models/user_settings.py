# models/user_settings.py

from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, String, DateTime

from models.base import Base


class UserSettings(Base):
    """Настройки пользователя для напоминаний и интерфейса"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)

    # Настройки напоминаний
    reminders_enabled = Column(Boolean, default=True)
    reminder_hour = Column(Integer, default=20)
    reminder_minute = Column(Integer, default=0)
    notification_sound = Column(Boolean, default=True)
    last_notification_sent = Column(DateTime, nullable=True)

    # Настройки интерфейса
    theme = Column(String(20), default="dark")  # dark, light, ocean, forest, sunset
    language = Column(String(10), default="ru")  # ru, en, es, fr, de

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings reminders={self.reminders_enabled} theme={self.theme} language={self.language}>"