from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.completion import HabitCompletion


def calculate_current_streak(session: Session, habit_id: int) -> int:
    completions = session.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.date.desc()).all()  # Changed: completed_at -> date

    if not completions:
        return 0

    streak = 0
    # Get the most recent completion date
    expected_date = completions[0].date.date() if completions[0].date else None

    if not expected_date:
        return 0

    for comp in completions:
        comp_date = comp.date.date() if comp.date else None
        if comp_date and comp_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break

    return streak


def calculate_best_streak(session: Session, habit_id: int) -> int:
    # Get all completions ordered by date
    completions = session.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.date.asc()).all()  # Changed: completed_at -> date

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
            # Same day, skip
            continue
        else:
            current_streak = 1

        last_date = comp_date
        best_streak = max(best_streak, current_streak)

    return best_streak