# models/completion.py (исправленная версия)

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.base import Base


class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed = Column(Boolean, default=True)
    note = Column(String(500), default="")

    habit = relationship("Habit", back_populates="completions")

    @property
    def completed_at(self):
        """Alias for date to maintain compatibility"""
        return self.date

    @completed_at.setter
    def completed_at(self, value):
        self.date = value

    def __repr__(self):
        return f"<HabitCompletion {self.habit_id} on {self.date.date()}>"