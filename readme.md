habit_tracker/
├── main.py
├── requirements.txt
├── README.md
├── database.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── habit.py
│   ├── completion.py
│   ├── user_progress.py
│   └── user_settings.py          # ← расширена
├── ui/
│   ├── __init__.py
│   ├── main_window.py            # ← обновлён
│   ├── dashboard_widget.py
│   ├── habit_list_widget.py
│   ├── pomodoro_widget.py
│   ├── reminder_settings_widget.py
│   ├── stats_widget.py
│   ├── settings_widget.py        # ← НОВЫЙ
│   ├── locale.py                 # ← НОВЫЙ (опционально)
│   └── dialogs/
│       ├── __init__.py
│       └── habit_dialog.py
├── utils/
│   ├── __init__.py
│   ├── reminder.py
│   └── streak
├── data/
│   └── seed.py
