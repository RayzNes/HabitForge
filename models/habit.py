# models/habit.py (исправленная версия)

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from models.base import Base


class Frequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#4CAF50")  # hex color
    icon = Column(String(50), default="⭐")
    category = Column(String(50), default="Общее")
    frequency = Column(SQLEnum(Frequency), default=Frequency.DAILY)
    days_of_week = Column(String(20), default="")  # например "1,2,3,4,5"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Habit {self.name}>"