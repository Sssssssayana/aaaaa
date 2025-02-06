import os

# Включаем поддержку ANSI в Windows
os.system('color')

class Colors:
    BLUE = '\033[94m'  # Синий
    GREEN = '\033[92m'  # Зеленый
    RED = '\033[91m'  # Красный
    YELLOW = '\033[93m'  # Желтый
    ENDC = '\033[0m'  # Сброс цвета 