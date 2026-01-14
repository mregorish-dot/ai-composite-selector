"""
Главный файл для запуска Streamlit приложения
Используется для деплоя на Streamlit Cloud
"""
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Импортируем основной модуль
from app import *

