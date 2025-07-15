import os

from dotenv import load_dotenv

# Загружаем переменные из .env перед импортом приложения
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
