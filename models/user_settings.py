# models/user_settings.py

from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, String, DateTime, Time

from models.base import Base


class UserSettings(Base):
    """Настройки пользователя для напоминаний"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    reminders_enabled = Column(Boolean, default=True)
    reminder_hour = Column(Integer, default=20)
    reminder_minute = Column(Integer, default=0)
    notification_sound = Column(Boolean, default=True)
    last_notification_sent = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings reminders={self.reminders_enabled} at {self.reminder_hour:02d}:{self.reminder_minute:02d}>"