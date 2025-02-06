# Пути к папкам
USER_FOLDER = 'users'
TEXT_FOLDER = 'user_text'
ENCRYPTED_FOLDER = 'encrypted_text'
DECRYPTED_FOLDER = 'decrypted_text'
QUERY_FOLDER = 'query_history'

# URL endpoints
BASE_URL = 'http://127.0.0.1:8000'
AUTH_URL = f'{BASE_URL}/auth'
REGISTER_URL = f'{BASE_URL}/register'
CHANGE_PASSWORD_URL = f'{BASE_URL}/change_password'
ADD_TEXT_URL = f'{BASE_URL}/add_text'
VIEW_ALL_TEXTS_URL = f'{BASE_URL}/view_all_texts'
VIEW_ONE_TEXT_URL = f'{BASE_URL}/view_one_text'
VIEW_ENCRYPTED_TEXTS_URL = f'{BASE_URL}/view_encrypted_texts'
VIEW_DECRYPTED_TEXTS_URL = f'{BASE_URL}/view_decrypted_texts'
DELETE_TEXT_URL = f'{BASE_URL}/delete_text'
CHANGE_TEXT_URL = f'{BASE_URL}/change_the_text'
ENCRYPT_URL = f'{BASE_URL}/cipher_encrypt'
DECRYPT_URL = f'{BASE_URL}/cipher_decrypt'
QUERY_HISTORY_URL = f'{BASE_URL}/query_history'
DELETE_HISTORY_URL = f'{BASE_URL}/delete_query_history'
EXIT_URL = f'{BASE_URL}/exit'

# Сообщения пользователю
SUCCESS_AUTH = "Авторизация успешна!"
SUCCESS_REGISTER = "Регистрация успешна!"
ERROR_USER_NOT_FOUND = "Пользователь не найден"
ERROR_WRONG_PASSWORD = "Неверный пароль"
ERROR_EMPTY_LOGIN = "Логин не может быть пустым"
ERROR_INVALID_PASSWORD = "Пароль должен содержать минимум 8 символов, буквы, цифры и специальные символы"

# Требования к паролю
MIN_PASSWORD_LENGTH = 8
SPECIAL_CHARS = "!@#$%^&*()_-+=<>?/:;.,~"
# ... другие сообщения 