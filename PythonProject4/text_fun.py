from type_of_requests import send_get
from colors import Colors
from typing import List
import math
import random
import json


def text_selection(url: str, user: bytes, header: str, action: str) -> tuple[str, List[int]]:
    """Возвращает выбранный текст и ключи шифрования"""
    response = send_get(url, data=user)
    
    if "detail" in response:
        print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
        return "", []

    texts = response.get('texts', [])
    if not texts:
        print(f"{Colors.YELLOW}Нет доступных текстов{Colors.ENDC}")
        return "", []

    print(f"\n{Colors.BLUE}{header}{Colors.ENDC}")
    for index, text_info in enumerate(texts, start=1):
        content = text_info.get('content', '')
        # Если контент является JSON строкой, извлекаем только текст
        try:
            content_json = json.loads(content)
            if isinstance(content_json, dict) and 'text' in content_json:
                print(f"{index}. {content_json['text']}")
                continue
        except json.JSONDecodeError:
            pass
        print(f"{index}. {content}")

    while True:
        try:
            text_number = int(input(f"Введите номер текста, который хотите {action} (0 для отмены): "))
            if text_number == 0:
                return "", []
            if 1 <= text_number <= len(texts):
                content = texts[text_number - 1].get('content', '')
                try:
                    # Пробуем распарсить JSON, если это зашифрованный текст
                    content_json = json.loads(content)
                    if isinstance(content_json, dict):
                        return content_json.get('text', ''), content_json.get('key', [])
                except json.JSONDecodeError:
                    return content, []
            else:
                print(f"{Colors.RED}Ошибка: Введите число от 1 до {len(texts)}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")


def all_texts(url: str, user: bytes, header: str):
    response = send_get(url=url, data=user)
    if "detail" in response:
        print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
        return False
    print(header)
    texts = response.get('texts', [])
    for index, text in enumerate(texts, start=1):
        print(f"{index}. {text}")
    return True


def text_one(url: str, user: bytes):
    response = send_get(url, data=user)
    if "detail" in response:
        print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
        return False
    texts = response.get('texts', [])
    if not texts:
        return False
    print("Выберите текст:")
    for index, text in enumerate(texts, start=1):
        print(f"{index}. {text}")
    while True:
        try:
            text_number = int(input("Введите номер текста: "))
            if 1 <= text_number <= len(texts):
                return text_number
            else:
                print(f"Введите число от 1 до {len(texts)}.")
        except ValueError:
            print("Введите корректное число.")


def del_text(url: str, user: bytes, header: str):
    response = send_get(url=url, data=user)
    print(header)
    texts = response.get('texts', [])
    for index, text in enumerate(texts, start=1):
        print(f"{index}. {text}")
    return texts


def text_verification(text):
    if not text:
        print("Выберите, пожалуйста, другое действие.")
        return False
    return True


def get_matrix_size(text: str) -> tuple:
    """Определяет оптимальный размер матрицы для текста"""
    text_len = len(text)
    sqrt = math.ceil(math.sqrt(text_len))

    # Находим оптимальные размеры матрицы
    for cols in range(sqrt, text_len + 1):
        rows = math.ceil(text_len / cols)
        if rows <= cols:  # Предпочитаем матрицу, где строк не больше чем столбцов
            return rows, cols
    return sqrt, sqrt


def generate_random_key(size: int) -> list:
    """Генерирует случайную перестановку заданного размера"""
    numbers = list(range(1, size + 1))
    random.shuffle(numbers)
    return numbers


def get_keys(text: str) -> List[int]:
    """Генерирует ключи для шифрования текста"""
    rows, cols = get_matrix_size(text)
    print(f"\nАвтоматически определен размер матрицы: {rows}x{cols}")
    
    # Генерируем ключи для столбцов (1..cols)
    col_key = generate_random_key(cols)
    print(f"Сгенерированная перестановка для столбцов: {col_key}")
    
    # Генерируем ключи для строк (1..rows)
    row_key = generate_random_key(rows)
    print(f"Сгенерированная перестановка для строк: {row_key}")
    
    # Объединяем ключи в один список
    return col_key + row_key


def create_matrix(text: str, cols: int) -> List[List[str]]:
    """Создает матрицу из текста"""
    # Дополняем текст пробелами до размера матрицы
    text_len = len(text)
    rows = math.ceil(text_len / cols)
    total_size = rows * cols
    text = text.ljust(total_size)
    
    # Создаем матрицу
    matrix = []
    for i in range(0, total_size, cols):
        matrix.append(list(text[i:i + cols]))
    return matrix


def apply_permutation(matrix: List[List[str]], perm: List[int], is_rows: bool = False) -> List[List[str]]:
    """Применяет перестановку к матрице"""
    if is_rows:
        # Перестановка строк
        return [matrix[i-1] for i in perm]
    else:
        # Перестановка столбцов
        return [[row[i-1] for i in perm] for row in matrix]


def matrix_to_text(matrix: List[List[str]]) -> str:
    """Преобразует матрицу в текст"""
    return ''.join(''.join(row) for row in matrix)


def validate_permutation(perm: list, size: int) -> bool:
    """Проверяет корректность перестановки"""
    if len(perm) != size:
        return False
    return sorted(perm) == list(range(1, size + 1))


def encrypt(text: str, key: List[int]) -> str:
    """Шифрование методом двойной табличной перестановки"""
    # Определяем размеры матрицы
    rows, cols = get_matrix_size(text)
    
    # Разделяем ключ на перестановки для столбцов и строк
    col_perm = key[:cols]
    row_perm = key[cols:]
    
    # Проверяем корректность ключей
    if not validate_permutation(col_perm, cols) or not validate_permutation(row_perm, rows):
        raise ValueError("Неверный формат ключа перестановки")
    
    # Создаем матрицу из текста
    matrix = create_matrix(text, cols)
    
    # Применяем перестановки
    matrix = apply_permutation(matrix, col_perm)
    matrix = apply_permutation(matrix, row_perm, True)
    
    # Преобразуем матрицу обратно в текст
    return matrix_to_text(matrix)


def decrypt(text: str, key: List[int]) -> str:
    """Дешифрование методом двойной табличной перестановки"""
    # Определяем размеры матрицы
    rows, cols = get_matrix_size(text)
    
    # Разделяем ключ на перестановки
    col_perm = key[:cols]
    row_perm = key[cols:]
    
    if not validate_permutation(col_perm, cols) or not validate_permutation(row_perm, rows):
        raise ValueError("Неверный формат ключа перестановки")

    # Создаем матрицу из текста
    matrix = create_matrix(text, cols)

    # Создаем обратные перестановки
    inv_col_perm = [col_perm.index(i + 1) + 1 for i in range(cols)]
    inv_row_perm = [row_perm.index(i + 1) + 1 for i in range(rows)]

    # Применяем обратные перестановки в обратном порядке
    matrix = apply_permutation(matrix, inv_row_perm, True)
    matrix = apply_permutation(matrix, inv_col_perm)

    # Преобразуем матрицу в текст и удаляем добавленные пробелы
    return matrix_to_text(matrix).rstrip()
