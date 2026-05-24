# utils/streak.py (исправленная версия с часовыми поясами)

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.completion import HabitCompletion


def calculate_current_streak(session: Session, habit_id: int) -> int:
    """Рассчитать текущую серию выполнения привычки"""
    completions = session.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.date.desc()).all()

    if not completions:
        return 0

    streak = 0
    today = datetime.now(timezone.utc).date()

    # Проверяем, выполнена ли привычка сегодня
    last_completion = completions[0].date.date() if completions[0].date else None

    if last_completion != today:
        # Если сегодня не выполнено, серия прервана
        # Но проверяем, может быть последнее выполнение было вчера?
        if last_completion == today - timedelta(days=1):
            pass  # Продолжаем проверку
        else:
            return 0

    expected_date = today
    for comp in completions:
        comp_date = comp.date.date() if comp.date else None
        if comp_date and comp_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break

    return streak


def calculate_best_streak(session: Session, habit_id: int) -> int:
    """Рассчитать лучшую серию выполнения привычки"""
    completions = session.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.date.asc()).all()

    if not completions:
        return 0

    best_streak = 0
    current_streak = 0
    last_date = None

    for comp in completions:
        comp_date = comp.date.date() if comp.date else None
        if comp_date is None:
            continue

        if last_date is None:
            current_streak = 1
        elif (comp_date - last_date).days == 1:
            current_streak += 1
        elif (comp_date - last_date).days == 0:
            # Тот же день, пропускаем
            continue
        else:
            current_streak = 1

        last_date = comp_date
        best_streak = max(best_streak, current_streak)

    return best_streak


def get_completion_streak_info(session: Session, habit_id: int) -> dict:
    """Получить полную информацию о сериях"""
    return {
        "current_streak": calculate_current_streak(session, habit_id),
        "best_streak": calculate_best_streak(session, habit_id),
        "total_completions": session.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id
        ).count()
    }