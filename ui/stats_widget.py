# ui/stats_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta, date
import calendar
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

from sqlalchemy.orm import Session
from models.habit import Habit
from models.completion import HabitCompletion
from utils.streak import calculate_current_streak, calculate_best_streak


class StatsWidget(QWidget):
    """Виджет со статистикой: календарь активности, графики, серии"""

    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.current_date = datetime.now().date()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        header = QLabel("📊 Статистика привычек")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Строка с сериями
        streaks_layout = QHBoxLayout()

        self.current_streak_label = QLabel("🔥 Текущая серия: --")
        self.current_streak_label.setStyleSheet(
            "font-size: 16px; background-color: #2D2D2D; padding: 15px; border-radius: 10px;")
        streaks_layout.addWidget(self.current_streak_label)

        self.best_streak_label = QLabel("🏆 Лучшая серия: --")
        self.best_streak_label.setStyleSheet(
            "font-size: 16px; background-color: #2D2D2D; padding: 15px; border-radius: 10px;")
        streaks_layout.addWidget(self.best_streak_label)

        layout.addLayout(streaks_layout)

        # Контейнер для графиков
        charts_layout = QHBoxLayout()

        # Левая колонка - Категории
        category_frame = QFrame()
        category_frame.setStyleSheet("background-color: #2D2D2D; border-radius: 10px; padding: 10px;")
        category_layout = QVBoxLayout(category_frame)
        category_label = QLabel("📈 Выполнение по категориям")
        category_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        category_layout.addWidget(category_label)

        self.category_figure = plt.figure(figsize=(4, 3))
        self.category_canvas = FigureCanvas(self.category_figure)
        category_layout.addWidget(self.category_canvas)
        charts_layout.addWidget(category_frame)

        # Правая колонка - Прогресс за период
        progress_frame = QFrame()
        progress_frame.setStyleSheet("background-color: #2D2D2D; border-radius: 10px; padding: 10px;")
        progress_layout = QVBoxLayout(progress_frame)
        progress_label = QLabel("📅 Прогресс за неделю")
        progress_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        progress_layout.addWidget(progress_label)

        self.progress_figure = plt.figure(figsize=(4, 3))
        self.progress_canvas = FigureCanvas(self.progress_figure)
        progress_layout.addWidget(self.progress_canvas)
        charts_layout.addWidget(progress_frame)

        layout.addLayout(charts_layout)

        # Календарь активности (Heatmap)
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("background-color: #2D2D2D; border-radius: 10px; padding: 10px;")
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_header = QLabel("📆 Календарь активности (Heatmap)")
        calendar_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        calendar_layout.addWidget(calendar_header)

        self.calendar_figure = plt.figure(figsize=(8, 4))
        self.calendar_canvas = FigureCanvas(self.calendar_figure)
        calendar_layout.addWidget(self.calendar_canvas)
        layout.addWidget(calendar_frame)

        # Кнопка обновления
        from PySide6.QtWidgets import QPushButton
        refresh_btn = QPushButton("🔄 Обновить статистику")
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5BA0F2;
            }
        """)
        layout.addWidget(refresh_btn)

    def refresh(self):
        """Обновить все данные на виджете"""
        self.update_streaks()
        self.update_category_chart()
        self.update_progress_chart()
        self.update_calendar_heatmap()

    def update_streaks(self):
        """Обновить информацию о сериях"""
        habits = self.session.query(Habit).all()

        total_current_streak = 0
        total_best_streak = 0

        for habit in habits:
            total_current_streak += calculate_current_streak(self.session, habit.id)
            total_best_streak += calculate_best_streak(self.session, habit.id)

        # Также показываем максимальную серию по всем привычкам
        best_individual = 0
        current_individual = 0
        for habit in habits:
            best = calculate_best_streak(self.session, habit.id)
            curr = calculate_current_streak(self.session, habit.id)
            if best > best_individual:
                best_individual = best
            if curr > current_individual:
                current_individual = curr

        self.current_streak_label.setText(f"🔥 Текущая серия: {current_individual} дней")
        self.best_streak_label.setText(f"🏆 Лучшая серия: {best_individual} дней")

    def update_category_chart(self):
        """Обновить круговую диаграмму выполнения по категориям"""
        self.category_figure.clear()
        ax = self.category_figure.add_subplot(111)

        habits = self.session.query(Habit).all()
        category_completions = defaultdict(int)
        category_total = defaultdict(int)

        # Собираем статистику по категориям
        for habit in habits:
            completions_count = self.session.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit.id
            ).count()

            category_completions[habit.category] += completions_count
            category_total[habit.category] += 1  # каждая привычка считается как 1

        if not category_completions:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', color='white')
        else:
            categories = list(category_completions.keys())
            values = list(category_completions.values())

            colors = ['#4CAF50', '#2196F3', '#FF5722', '#9C27B0', '#FFC107', '#E91E63']
            wedges, texts, autotexts = ax.pie(
                values,
                labels=categories,
                autopct='%1.1f%%',
                colors=colors[:len(categories)],
                startangle=90
            )

            for text in texts:
                text.set_color('white')
            for autotext in autotexts:
                autotext.set_color('white')

        ax.set_title('Выполнение по категориям', color='white')
        self.category_figure.set_facecolor('#2D2D2D')
        ax.set_facecolor('#2D2D2D')
        self.category_canvas.draw()

    def update_progress_chart(self):
        """Обновить столбчатую диаграмму прогресса за неделю"""
        self.progress_figure.clear()
        ax = self.progress_figure.add_subplot(111)

        # Получаем даты за последние 7 дней
        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        completions_per_day = []

        for date in dates:
            start = datetime(date.year, date.month, date.day)
            end = start + timedelta(days=1)

            count = self.session.query(HabitCompletion).filter(
                HabitCompletion.date >= start,
                HabitCompletion.date < end
            ).count()
            completions_per_day.append(count)

        bars = ax.bar(day_names, completions_per_day, color='#4CAF50', alpha=0.8)

        # Добавляем значения на столбцы
        for bar, value in zip(bars, completions_per_day):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(value), ha='center', va='bottom', color='white')

        ax.set_xlabel('День недели', color='white')
        ax.set_ylabel('Выполнено привычек', color='white')
        ax.set_title('Ежедневная активность', color='white')
        ax.tick_params(colors='white')
        ax.set_ylim(0, max(completions_per_day + [5]) + 2)

        self.progress_figure.set_facecolor('#2D2D2D')
        ax.set_facecolor('#2D2D2D')
        self.progress_canvas.draw()

    def update_calendar_heatmap(self):
        """Обновить тепловую карту календаря активности"""
        self.calendar_figure.clear()

        # Получаем данные за последние 12 недель
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=84)  # 12 недель

        # Получаем все завершения за период
        completions = self.session.query(HabitCompletion).filter(
            HabitCompletion.date >= datetime(start_date.year, start_date.month, start_date.day),
            HabitCompletion.date < datetime(end_date.year, end_date.month, end_date.day) + timedelta(days=1)
        ).all()

        # Группируем по дням
        completions_by_date = defaultdict(int)
        for comp in completions:
            date_key = comp.date.date() if hasattr(comp.date, 'date') else comp.date
            completions_by_date[date_key] += 1

        # Создаём матрицу 7x12 (дни недели x недели)
        heatmap_data = [[0 for _ in range(12)] for _ in range(7)]

        current_date = start_date
        week = 0

        while current_date <= end_date and week < 12:
            weekday = current_date.weekday()  # Monday=0, Sunday=6
            completions_count = completions_by_date.get(current_date, 0)

            # Нормализуем значение (0-5+ completions)
            value = min(completions_count, 5)
            heatmap_data[weekday][week] = value

            current_date += timedelta(days=1)
            if current_date.weekday() == 0:  # Новая неделя
                week += 1

        # Рисуем тепловую карту
        ax = self.calendar_figure.add_subplot(111)

        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=5)

        # Настройка осей
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        ax.set_yticks(range(7))
        ax.set_yticklabels(days)
        ax.set_xticks(range(12))

        # Метки недель (номера недель)
        week_labels = []
        current = start_date
        for i in range(12):
            week_num = current.isocalendar()[1]
            week_labels.append(f'Нед {week_num}')
            current += timedelta(days=7)
        ax.set_xticklabels(week_labels, rotation=45, ha='right')

        ax.set_title('Тепловая карта активности (последние 12 недель)', color='white')
        ax.tick_params(colors='white')

        # Добавляем цветовую шкалу
        cbar = self.calendar_figure.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Выполнений в день', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

        # Добавляем значения в ячейки
        for i in range(7):
            for j in range(12):
                if heatmap_data[i][j] > 0:
                    text_color = 'white' if heatmap_data[i][j] > 3 else 'black'
                    ax.text(j, i, str(heatmap_data[i][j]), ha='center', va='center',
                            color=text_color, fontsize=8)

        self.calendar_figure.set_facecolor('#2D2D2D')
        ax.set_facecolor('#2D2D2D')
        self.calendar_canvas.draw()