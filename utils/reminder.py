# utils/reminder.py (исправленная версия)

import threading
import time
from datetime import datetime, time as dt_time, timezone
from typing import List, Dict, Any
import logging
from plyer import notification

from sqlalchemy.orm import Session
from models.habit import Habit, Frequency
from models.completion import HabitCompletion
from models.user_settings import UserSettings


class ReminderService:
    """Сервис для управления напоминаниями о привычках"""

    def __init__(self, session: Session):
        self.session = session
        self.check_interval = 60  # проверка каждые 60 секунд
        self.running = False
        self.thread = None
        self.reminders_enabled = True
        self.reminder_time = dt_time(20, 0)  # 20:00 по умолчанию
        self._stop_event = threading.Event()  # Добавляем событие для остановки

    def start(self):
        """Запустить сервис напоминаний в фоновом потоке"""
        if self.running:
            return

        self.running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logging.info("Reminder service started")

    def stop(self):
        """Остановить сервис напоминаний"""
        self.running = False
        self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
        logging.info("Reminder service stopped")

    def _run(self):
        """Основной цикл проверки напоминаний"""
        last_daily_check = None

        while self.running and not self._stop_event.is_set():
            try:
                current_time = datetime.now(timezone.utc)

                # Проверка дневных напоминаний (каждый час)
                self._check_habits_reminder()

                # Ежедневная проверка в указанное время
                if self.reminders_enabled:
                    if (last_daily_check is None or
                            current_time.date() != last_daily_check.date()):

                        # Проверяем, наступило ли время напоминания
                        reminder_datetime = datetime.combine(
                            current_time.date(),
                            self.reminder_time,
                            tzinfo=timezone.utc
                        )

                        if current_time >= reminder_datetime:
                            self._send_daily_reminder()
                            last_daily_check = current_time

                # Используем _stop_event.wait() вместо time.sleep()
                self._stop_event.wait(timeout=self.check_interval)

            except Exception as e:
                logging.error(f"Error in reminder service: {e}")
                self._stop_event.wait(timeout=self.check_interval)

    def _check_habits_reminder(self):
        """Проверить привычки, требующие выполнения сегодня"""
        db = None
        try:
            # Получаем новую сессию для потока
            from database import SessionLocal
            db = SessionLocal()

            habits = db.query(Habit).all()
            habits_due = []

            for habit in habits:
                if self._is_habit_due_today(habit, db):
                    # Проверяем, выполнена ли уже привычка сегодня
                    if not self._is_habit_completed_today(habit.id, db):
                        habits_due.append(habit)

            if habits_due:
                self._send_habits_reminder(habits_due)

        except Exception as e:
            logging.error(f"Error checking habits due: {e}")
        finally:
            if db:
                db.close()

    def _is_habit_due_today(self, habit: Habit, session: Session) -> bool:
        """Проверить, должна ли привычка быть выполнена сегодня"""
        today = datetime.now(timezone.utc).date()

        if habit.frequency == Frequency.DAILY:
            return True

        elif habit.frequency == Frequency.WEEKLY:
            if habit.days_of_week:
                weekdays = [int(d.strip()) for d in habit.days_of_week.split(',') if d.strip()]
                today_weekday = today.isoweekday()  # Monday=1, Sunday=7
                return today_weekday in weekdays
            return True  # По умолчанию - каждый день

        return False

    def _is_habit_completed_today(self, habit_id: int, session: Session) -> bool:
        """Проверить, выполнена ли привычка сегодня"""
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        completion = session.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.date >= today_start
        ).first()

        return completion is not None

    def _send_habits_reminder(self, habits: List[Habit]):
        """Отправить напоминание о привычках"""
        if not self.reminders_enabled:
            return

        habit_list = '\n'.join([f"  • {habit.icon} {habit.name}" for habit in habits[:5]])

        if len(habits) > 5:
            habit_list += f"\n  • и {len(habits) - 5} других..."

        try:
            notification.notify(
                title='⏰ Напоминание о привычках',
                message=f'Сегодня ещё не выполнены:\n{habit_list}',
                app_name='HabitForge',
                timeout=10
            )
            logging.info(f"Sent reminder for {len(habits)} habits")
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")

    def _send_daily_reminder(self):
        """Отправить ежедневное итоговое напоминание"""
        db = None
        try:
            from database import SessionLocal
            db = SessionLocal()

            now = datetime.now(timezone.utc)
            today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

            # Получаем все привычки
            habits = db.query(Habit).all()
            total_habits = len(habits)
            completed_today = 0

            for habit in habits:
                if self._is_habit_completed_today(habit.id, db):
                    completed_today += 1

            if total_habits > 0:
                progress = (completed_today / total_habits) * 100

                if completed_today < total_habits:
                    remaining = total_habits - completed_today
                    notification.notify(
                        title='📊 Итоги дня в HabitForge',
                        message=f'Сегодня выполнено {completed_today} из {total_habits} привычек ({progress:.0f}%)\nОсталось: {remaining} привычек',
                        app_name='HabitForge',
                        timeout=10
                    )
                else:
                    notification.notify(
                        title='🎉 Отличная работа!',
                        message=f'Вы выполнили все {total_habits} привычек сегодня! +10 XP за каждую!',
                        app_name='HabitForge',
                        timeout=10
                    )

        except Exception as e:
            logging.error(f"Error sending daily reminder: {e}")
        finally:
            if db:
                db.close()

    def send_test_notification(self):
        """Отправить тестовое уведомление"""
        try:
            notification.notify(
                title='HabitForge - Напоминания работают!',
                message='Это тестовое уведомление. Напоминания настроены правильно.',
                app_name='HabitForge',
                timeout=5
            )
            return True
        except Exception as e:
            logging.error(f"Test notification failed: {e}")
            return False

    def set_reminder_time(self, hour: int, minute: int):
        """Установить время ежедневного напоминания"""
        self.reminder_time = dt_time(hour, minute)
        logging.info(f"Daily reminder time set to {hour:02d}:{minute:02d}")

    def toggle_reminders(self, enabled: bool):
        """Включить/выключить напоминания"""
        self.reminders_enabled = enabled
        logging.info(f"Reminders {'enabled' if enabled else 'disabled'}")