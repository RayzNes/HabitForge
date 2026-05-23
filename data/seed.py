from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from database import get_db
from models.habit import Habit, Frequency
from models.user_progress import UserProgress
from models.completion import HabitCompletion


def seed_demo_data():
    db: Session = get_db()

    try:
        # Проверяем, есть ли уже данные
        if db.query(Habit).first():
            logging.info("Демонстрационные данные уже существуют")
            return

        # Создаём прогресс пользователя
        progress = UserProgress()
        db.add(progress)

        # Демо-привычки
        habits = [
            Habit(
                name="Пить воду",
                color="#4CAF50",
                icon="💧",
                category="Здоровье",
                frequency=Frequency.DAILY
            ),
            Habit(
                name="Читать 30 минут",
                color="#2196F3",
                icon="📚",
                category="Развитие",
                frequency=Frequency.DAILY
            ),
            Habit(
                name="Спорт",
                color="#FF5722",
                icon="🏋️",
                category="Здоровье",
                frequency=Frequency.DAILY
            ),
            Habit(
                name="Медитация",
                color="#9C27B0",
                icon="🧘",
                category="Ментальное здоровье",
                frequency=Frequency.DAILY
            ),
        ]

        db.add_all(habits)
        db.commit()

        # Добавляем несколько выполнений
        today = datetime.utcnow()
        for habit in habits:
            for i in range(5):
                completion = HabitCompletion(
                    habit_id=habit.id,
                    date=today - timedelta(days=i),
                    completed=True
                )
                db.add(completion)

        db.commit()
        logging.info("Демонстрационные данные были успешно обработаны")

    except Exception as e:
        logging.error(f"Error seeding demo data: {e}")
        db.rollback()
    finally:
        db.close()