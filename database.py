# database.py (обновленная версия)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base
import logging

DATABASE_URL = "sqlite:///habits.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Получить новую сессию БД"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def init_db():
    """Создать все таблицы"""
    try:
        # Импортируем все модели для регистрации в Base.metadata
        from models import Habit, HabitCompletion, UserProgress, UserSettings
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")

        # Создаём настройки по умолчанию, если их нет
        db = SessionLocal()
        if not db.query(UserSettings).first():
            default_settings = UserSettings()
            db.add(default_settings)
            db.commit()
            logging.info("Default user settings created")
        db.close()

    except Exception as e:
        logging.error(f"Database initialization error: {e}")