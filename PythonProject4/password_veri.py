import curses
from password_input import getpass_with_stars
from colors import Colors
from constants import MIN_PASSWORD_LENGTH, SPECIAL_CHARS


def get_password():
    """Получение и проверка пароля с маскировкой звездочками"""
    while True:
        try:
            # Пробуем использовать curses для Unix-подобных систем
            password = curses.wrapper(getpass_with_stars)
            password_confirm = curses.wrapper(getpass_with_stars, "Подтвердите пароль: ")
        except:
            # Если curses недоступен, используем вариант для Windows
            password = getpass_with_stars()
            password_confirm = getpass_with_stars("Подтвердите пароль: ")

        if password != password_confirm:
            print(f"{Colors.RED}Ошибка: Пароли не совпадают! Попробуйте снова.{Colors.ENDC}")
            continue
        if not complex_password(password):
            continue
        return password

def complex_password(password):
    """Проверка пароля на сложность с выводом ошибок"""
    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"{Colors.RED}Ошибка: Пароль должен быть не менее {MIN_PASSWORD_LENGTH} символов{Colors.ENDC}")
        return False
    if not any(char.isalpha() for char in password):
        print(f"{Colors.RED}Ошибка: Пароль должен содержать буквы (AaBb){Colors.ENDC}")
        return False
    if not any(char.isdigit() for char in password):
        print(f"{Colors.RED}Ошибка: Пароль должен содержать цифры (1234){Colors.ENDC}")
        return False
    if not any(char in SPECIAL_CHARS for char in password):
        print(f"{Colors.RED}Ошибка: Пароль должен содержать специальные символы ({SPECIAL_CHARS}){Colors.ENDC}")
        return False
    return True

def complex_password_s(password: str) -> bool:
    """Проверка пароля на сложность на сервере (без вывода ошибок)"""
    return (len(password) >= MIN_PASSWORD_LENGTH 
            and any(char.isalpha() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in SPECIAL_CHARS for char in password))

def validate_password(password: str) -> tuple[bool, list[str]]:
    """
    Проверяет пароль на соответствие требованиям безопасности.
    Возвращает кортеж (is_valid, errors).
    """
    errors = []
    
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Пароль должен быть не менее {MIN_PASSWORD_LENGTH} символов")
        
    if not any(char.isalpha() for char in password):
        errors.append("Пароль должен содержать буквы (AaBb)")
        
    if not any(char.isdigit() for char in password):
        errors.append("Пароль должен содержать цифры (1234)")
        
    if not any(char in SPECIAL_CHARS for char in password):
        errors.append(f"Пароль должен содержать специальные символы ({SPECIAL_CHARS})")
        
    return (len(errors) == 0, errors) 