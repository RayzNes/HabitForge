# ui/dashboard_widget.py (улучшенная версия)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QProgressBar, QGridLayout, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPainter, QBrush, QColor, QPen, QLinearGradient, QRadialGradient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from datetime import datetime, timedelta
from collections import defaultdict
import random
import math

from models.habit import Habit
from models.completion import HabitCompletion
from models.user_progress import UserProgress
from utils.streak import calculate_current_streak, calculate_best_streak


class HabitTreeWidget(QWidget):
    """Виджет визуализации 'Дерево привычек' - растёт с прогрессом"""

    def __init__(self, progress_percentage=0, parent=None):
        super().__init__(parent)
        self.progress_percentage = progress_percentage  # 0-100
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
        self.setStyleSheet("background-color: transparent;")

    def set_progress(self, percentage):
        """Обновить прогресс дерева"""
        self.progress_percentage = min(100, max(0, percentage))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width // 2
        ground_y = height - 40

        # Фон (небо)
        sky_gradient = QLinearGradient(0, 0, 0, height)
        sky_gradient.setColorAt(0, QColor(30, 60, 90))
        sky_gradient.setColorAt(1, QColor(20, 40, 60))
        painter.fillRect(0, 0, width, height, sky_gradient)

        # Солнце
        sun_radius = 30
        sun_gradient = QRadialGradient(center_x - 50, 50, sun_radius)
        sun_gradient.setColorAt(0, QColor(255, 200, 100))
        sun_gradient.setColorAt(1, QColor(255, 150, 50))
        painter.setBrush(QBrush(sun_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - 80, 20, sun_radius, sun_radius)

        # Земля/трава
        ground_gradient = QLinearGradient(0, ground_y, 0, height)
        ground_gradient.setColorAt(0, QColor(34, 139, 34))
        ground_gradient.setColorAt(1, QColor(20, 100, 20))
        painter.fillRect(0, ground_y, width, height - ground_y, ground_gradient)

        # Ствол дерева
        trunk_width = max(15, int(30 * (self.progress_percentage / 100)))
        trunk_height = int(80 * (0.5 + self.progress_percentage / 100))
        trunk_x = center_x - trunk_width // 2
        trunk_y = ground_y - trunk_height

        trunk_gradient = QLinearGradient(trunk_x, trunk_y, trunk_x + trunk_width, trunk_y)
        trunk_gradient.setColorAt(0, QColor(101, 67, 33))
        trunk_gradient.setColorAt(1, QColor(139, 90, 43))
        painter.setBrush(QBrush(trunk_gradient))
        painter.drawRect(trunk_x, trunk_y, trunk_width, trunk_height)

        # Корни
        root_count = int(3 + self.progress_percentage / 20)
        for i in range(root_count):
            angle = -30 + (i * 60 / root_count)
            root_length = 20 + self.progress_percentage / 5
            end_x = trunk_x + trunk_width // 2 + math.cos(math.radians(angle)) * root_length
            end_y = ground_y + math.sin(math.radians(angle)) * 15
            painter.setPen(QPen(QColor(101, 67, 33), 3))
            painter.drawLine(trunk_x + trunk_width // 2, ground_y, end_x, end_y)

        # Крона дерева (растёт с прогрессом)
        crown_size = 60 + (self.progress_percentage * 1.5)
        crown_y = trunk_y - crown_size // 3

        # Листья - несколько слоёв
        leaf_colors = [
            QColor(34, 139, 34),
            QColor(50, 205, 50),
            QColor(60, 179, 113),
            QColor(144, 238, 144),
            QColor(152, 251, 152)
        ]

        num_layers = int(2 + self.progress_percentage / 25)
        for layer in range(num_layers):
            layer_size = crown_size * (1 - layer * 0.2)
            layer_y = crown_y + layer * 15
            color = leaf_colors[layer % len(leaf_colors)]

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 100, 0), 1))

            # Эллиптическая крона
            painter.drawEllipse(
                center_x - int(layer_size // 2),
                int(layer_y - layer_size // 2),
                int(layer_size),
                int(layer_size)
            )

        # Плоды (появляются при высоком прогрессе)
        if self.progress_percentage > 50:
            num_fruits = int(3 + (self.progress_percentage - 50) / 10)
            for i in range(num_fruits):
                angle = random.randint(0, 360)
                radius = crown_size // 2 - 10
                fruit_x = center_x + math.cos(math.radians(angle)) * radius
                fruit_y = crown_y + math.sin(math.radians(angle)) * radius

                # Яблоко/плод
                painter.setBrush(QBrush(QColor(255, 69, 0)))
                painter.drawEllipse(int(fruit_x - 5), int(fruit_y - 5), 10, 10)

                # Листик у плода
                painter.setBrush(QBrush(QColor(50, 205, 50)))
                painter.drawEllipse(int(fruit_x - 2), int(fruit_y - 8), 4, 6)

        # Стрелка прогресса (уровень)
        progress_bar_width = width - 40
        progress_bar_height = 8
        progress_bar_x = 20
        progress_bar_y = height - 20

        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height, 4, 4)

        painter.setBrush(QBrush(QColor(76, 175, 80)))
        painter.drawRoundedRect(progress_bar_x, progress_bar_y,
                                int(progress_bar_width * self.progress_percentage / 100),
                                progress_bar_height, 4, 4)

        # Текст прогресса
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(progress_bar_x + progress_bar_width + 5, progress_bar_y + 7,
                         f"{int(self.progress_percentage)}%")

        # Птички при хорошем прогрессе
        if self.progress_percentage > 40:
            for i in range(2):
                bird_x = center_x - 60 + i * 120
                bird_y = 40 + i * 30
                painter.setPen(QPen(QColor(200, 200, 200), 2))
                painter.drawLine(bird_x, bird_y, bird_x + 8, bird_y - 5)
                painter.drawLine(bird_x + 8, bird_y - 5, bird_x + 16, bird_y)


class CategoryProgressWidget(QWidget):
    """Виджет прогресса по категориям"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.title_label = QLabel("📊 Прогресс по категориям")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.title_label)

        self.categories_layout = QVBoxLayout()
        self.categories_layout.setSpacing(8)
        layout.addLayout(self.categories_layout)

        self.refresh()

    def refresh(self):
        # Очищаем старые виджеты
        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        habits = self.session.query(Habit).all()
        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day)

        # Группируем по категориям
        category_stats = defaultdict(lambda: {"total": 0, "completed": 0})

        for habit in habits:
            category_stats[habit.category]["total"] += 1

            # Проверяем, выполнена ли сегодня
            completion = self.session.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.date >= today_start
            ).first()
            if completion:
                category_stats[habit.category]["completed"] += 1

        # Цвета для категорий
        colors = ["#4CAF50", "#2196F3", "#FF5722", "#9C27B0", "#FFC107", "#E91E63", "#00BCD4", "#795548"]

        for i, (category, stats) in enumerate(category_stats.items()):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            frame_layout = QVBoxLayout(frame)

            # Заголовок категории
            cat_layout = QHBoxLayout()
            cat_icon = QLabel(self.get_category_icon(category))
            cat_icon.setStyleSheet("font-size: 20px;")
            cat_label = QLabel(category)
            cat_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            cat_layout.addWidget(cat_icon)
            cat_layout.addWidget(cat_label)
            cat_layout.addStretch()

            # Процент
            percentage = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            percent_label = QLabel(f"{percentage:.0f}%")
            percent_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            cat_layout.addWidget(percent_label)
            frame_layout.addLayout(cat_layout)

            # Прогресс-бар
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setValue(int(percentage))
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #555;
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {colors[i % len(colors)]};
                    border-radius: 5px;
                }}
            """)
            progress_bar.setFormat(f"{stats['completed']}/{stats['total']} выполнено")
            frame_layout.addWidget(progress_bar)

            self.categories_layout.addWidget(frame)

    def get_category_icon(self, category):
        """Получить иконку для категории"""
        icons = {
            "Здоровье": "💪",
            "Развитие": "📚",
            "Ментальное здоровье": "🧘",
            "Продуктивность": "⚡",
            "Общее": "⭐",
            "Health": "💪",
            "Learning": "📚",
            "Mindfulness": "🧘",
            "Productivity": "⚡",
            "General": "⭐"
        }
        return icons.get(category, "📌")


class MotivationalQuoteWidget(QWidget):
    """Виджет с мотивационными цитатами"""

    QUOTES = [
        ("💪", "Маленькие шаги каждый день приводят к большим результатам."),
        ("🔥", "Привычка — это то, что ты делаешь, когда не хочешь это делать."),
        ("⭐", "Дисциплина — это мост между целями и достижениями."),
        ("🌱", "Каждый день — это новая возможность стать лучше."),
        ("🎯", "Не жди идеального момента. Начни сейчас, с того, что имеешь."),
        ("🏆", "Успех — это сумма маленьких усилий, повторяемых день за днём."),
        ("📈", "Ты не обязан быть великим, чтобы начать, но ты обязан начать, чтобы стать великим."),
        ("🧠", "Сначала ты создаёшь привычки, а потом привычки создают тебя."),
        ("⚡", "Не сравнивай себя с другими. Сравнивай себя с тем, кем ты был вчера."),
        ("🎨", "Качество твоей жизни зависит от качества твоих привычек."),
        ("🌟", "Ты способен на большее, чем думаешь. Докажи это себе."),
        ("💎", "Самое трудное — это решение действовать. Остальное — упорство."),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.start_rotation()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.quote_frame = QFrame()
        self.quote_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        frame_layout = QVBoxLayout(self.quote_frame)

        self.quote_label = QLabel()
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setStyleSheet("""
            font-size: 16px;
            font-style: italic;
            padding: 10px;
        """)
        frame_layout.addWidget(self.quote_label)

        layout.addWidget(self.quote_frame)
        self.set_quote()

    def set_quote(self):
        """Выбрать случайную цитату"""
        icon, text = random.choice(self.QUOTES)
        self.quote_label.setText(f"{icon}  {text}")

    def start_rotation(self):
        """Запустить ротацию цитат каждые 30 секунд"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.set_quote)
        self.timer.start(30000)  # 30 секунд


class DashboardWidget(QWidget):
    """Улучшенный Dashboard с реальной статистикой"""

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        # Основной скроллируемый виджет
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Приветствие с динамическим временем
        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet("font-size: 28px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.greeting_label)

        # Верхняя панель с XP и уровнем
        xp_frame = QFrame()
        xp_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        xp_layout = QHBoxLayout(xp_frame)

        # Информация об уровне
        level_info = QVBoxLayout()
        self.level_label = QLabel("Уровень 1")
        self.level_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        level_info.addWidget(self.level_label)

        self.xp_bar = QProgressBar()
        self.xp_bar.setMaximum(100)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 10px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #FFD700;
                border-radius: 10px;
            }
        """)
        level_info.addWidget(self.xp_bar)
        xp_layout.addLayout(level_info)

        # Общая статистика
        stats_info = QHBoxLayout()
        stats_info.setSpacing(20)

        self.total_habits_label = self.create_stat_card("📋", "Всего привычек", "0")
        stats_info.addWidget(self.total_habits_label)

        self.completed_today_label = self.create_stat_card("✅", "Выполнено сегодня", "0")
        stats_info.addWidget(self.completed_today_label)

        self.streak_label = self.create_stat_card("🔥", "Текущая серия", "0")
        stats_info.addWidget(self.streak_label)

        xp_layout.addLayout(stats_info)
        layout.addWidget(xp_frame)

        # Дерево привычек
        tree_frame = QFrame()
        tree_frame.setStyleSheet("""
            QFrame {
                background-color: #1E2A1E;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        tree_layout = QVBoxLayout(tree_frame)
        tree_title = QLabel("🌳 Древо привычек")
        tree_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        tree_layout.addWidget(tree_title)

        self.tree_widget = HabitTreeWidget()
        tree_layout.addWidget(self.tree_widget)
        layout.addWidget(tree_frame)

        # Две колонки: категории и прогресс
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # Левая колонка - Категории
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        self.category_progress = CategoryProgressWidget(self.session)
        left_layout.addWidget(self.category_progress)
        columns_layout.addWidget(left_frame)

        # Правая колонка - Мотивация + дополнительная статистика
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)

        self.motivation_widget = MotivationalQuoteWidget()
        right_layout.addWidget(self.motivation_widget)

        # Ежедневная цель
        daily_goal_frame = QFrame()
        daily_goal_frame.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; padding: 10px;")
        daily_layout = QVBoxLayout(daily_goal_frame)
        daily_title = QLabel("🎯 Цель на сегодня")
        daily_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        daily_layout.addWidget(daily_title)

        self.daily_goal_progress = QProgressBar()
        self.daily_goal_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        daily_layout.addWidget(self.daily_goal_progress)
        right_layout.addWidget(daily_goal_frame)

        columns_layout.addWidget(right_frame)
        columns_layout.setStretch(0, 1)
        columns_layout.setStretch(1, 1)
        layout.addLayout(columns_layout)

        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Таймер для обновления приветствия
        self.greeting_timer = QTimer()
        self.greeting_timer.timeout.connect(self.update_greeting)
        self.greeting_timer.start(60000)  # Обновлять каждую минуту

    def create_stat_card(self, icon, title, value):
        """Создать карточку статистики"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11px; color: #aaa;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        value_label.setObjectName("value")
        layout.addWidget(value_label)

        return frame

    def update_greeting(self):
        """Обновить приветствие в зависимости от времени"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "🌅 Доброе утро, Хранитель привычек!"
        elif 12 <= hour < 18:
            greeting = "☀️ Добрый день, Хранитель привычек!"
        elif 18 <= hour < 23:
            greeting = "🌙 Добрый вечер, Хранитель привычек!"
        else:
            greeting = "🌃 Доброй ночи, Хранитель привычек! Не забывайте про отдых."

        self.greeting_label.setText(greeting)

    def refresh(self):
        """Обновить все данные на дашборде"""
        self.update_greeting()
        self.update_xp_and_level()
        self.update_habit_stats()
        self.category_progress.refresh()
        self.update_daily_goal()

        # Обновляем дерево привычек
        progress = self.calculate_overall_progress()
        self.tree_widget.set_progress(progress)

    def update_xp_and_level(self):
        """Обновить информацию об уровне и XP"""
        progress = self.session.query(UserProgress).first()

        if progress:
            next_level_xp = progress._xp_for_next_level()
            current_xp = progress.xp
            percentage = (current_xp / next_level_xp * 100) if next_level_xp > 0 else 0

            self.level_label.setText(f"⭐ Уровень {progress.level}")
            self.xp_bar.setValue(int(percentage))
            self.xp_bar.setFormat(f"{int(current_xp)}/{int(next_level_xp)} XP")
        else:
            self.level_label.setText("⭐ Уровень 1")
            self.xp_bar.setValue(0)
            self.xp_bar.setFormat("0/100 XP")

    def update_habit_stats(self):
        """Обновить общую статистику по привычкам"""
        habits = self.session.query(Habit).all()
        total_habits = len(habits)

        # Выполненные сегодня
        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day)
        completed_today = self.session.query(HabitCompletion).filter(
            HabitCompletion.date >= today_start
        ).count()

        # Общая серия (лучшая по всем привычкам)
        best_streak = 0
        for habit in habits:
            streak = calculate_current_streak(self.session, habit.id)
            if streak > best_streak:
                best_streak = streak

        # Обновляем карточки
        self.update_stat_card(self.total_habits_label, str(total_habits))
        self.update_stat_card(self.completed_today_label, str(completed_today))
        self.update_stat_card(self.streak_label, str(best_streak))

    def update_stat_card(self, card, value):
        """Обновить значение в карточке статистики"""
        value_label = card.findChild(QLabel, "value")
        if not value_label:
            value_label = card.findChildren(QLabel)[-1]
            value_label.setObjectName("value")
        value_label.setText(value)

    def update_daily_goal(self):
        """Обновить прогресс ежедневной цели"""
        habits = self.session.query(Habit).all()
        total = len(habits)

        if total == 0:
            self.daily_goal_progress.setValue(0)
            self.daily_goal_progress.setFormat("Нет привычек")
            return

        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day)

        completed = 0
        for habit in habits:
            completion = self.session.query(HabitCompletion).filter(
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.date >= today_start
            ).first()
            if completion:
                completed += 1

        percentage = (completed / total * 100) if total > 0 else 0
        self.daily_goal_progress.setValue(int(percentage))
        self.daily_goal_progress.setFormat(f"Выполнено {completed} из {total} привычек ({percentage:.0f}%)")

    def calculate_overall_progress(self):
        """Рассчитать общий прогресс пользователя (для дерева)"""
        habits = self.session.query(Habit).all()
        total_habits = len(habits)

        if total_habits == 0:
            return 0

        # Получаем прогресс из XP
        progress = self.session.query(UserProgress).first()
        xp_progress = 0
        if progress:
            next_level_xp = progress._xp_for_next_level()
            xp_progress = (progress.xp / next_level_xp * 100) if next_level_xp > 0 else 0

        # Также учитываем выполненные привычки сегодня
        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day)
        completed_today = self.session.query(HabitCompletion).filter(
            HabitCompletion.date >= today_start
        ).count()

        completed_percentage = (completed_today / total_habits * 100) if total_habits > 0 else 0

        # Комбинируем прогресс: 70% XP + 30% ежедневные привычки
        overall = (xp_progress * 0.7) + (completed_percentage * 0.3)
        return min(100, overall)