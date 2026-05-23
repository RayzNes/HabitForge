from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime

from models.base import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)
    level = Column(Integer, default=1)
    xp = Column(Float, default=0.0)
    total_xp_earned = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    def add_xp(self, amount: float):
        self.xp += amount
        self.total_xp_earned += amount
        self.last_updated = datetime.utcnow()

        # Level up logic
        while self.xp >= self._xp_for_next_level():
            self.level += 1
            self.xp -= self._xp_for_next_level()

    def _xp_for_next_level(self) -> float:
        return 100 * (1.5 ** (self.level - 1))

    def progress_percentage(self) -> float:
        return (self.xp / self._xp_for_next_level()) * 100 if self.level > 0 else 0

