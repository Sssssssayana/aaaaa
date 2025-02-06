import json, curses, os  # для хеширования пароля и пароля, чтобы его не было видно
from models import Change_Text_Request, Delete_Request, One_Text_Request, Cipher_Request, User, Change_Password_Request, \
    Text_Request, Token
from type_of_requests import send_delete, send_get, send_patch, send_post
from text_fun import all_texts, text_one, del_text, text_selection, get_keys, text_verification
from password_veri import get_password
from password_input import getpass_with_stars
from colors import Colors  # Изменить импорт

user_token = None  # глобальная переменная для хранения токена


# Добавим в начало файла константы для цветов
class Colors:
    BLUE = '\033[94m'  # Синий
    GREEN = '\033[92m'  # Зеленый
    RED = '\033[91m'  # Красный
    YELLOW = '\033[93m'  # Желтый
    ENDC = '\033[0m'  # Сброс цвета


# В начале программы
os.system('color')  # Включаем поддержку ANSI в Windows


def auth():
    global user_token
    while True:
        try:
            login = input("Введите логин: ")
            if not login.strip():
                print(f"{Colors.RED}Ошибка: Логин не может быть пустым. Попробуйте снова.{Colors.ENDC}")
                continue

            # Сначала проверяем существование пользователя
            check_data = User(login=login, password="temp", token='token').model_dump_json().encode('utf-8')
            check_response = send_get('http://127.0.0.1:8000/check_user', data=check_data)
            
            if "detail" in check_response:
                if "Пользователь не найден" in check_response["detail"]:
                    print(f"{Colors.YELLOW}Пользователь с логином '{login}' не найден.{Colors.ENDC}")
                    print(f"{Colors.YELLOW}Пожалуйста, зарегистрируйтесь.{Colors.ENDC}")
                    return False
                else:
                    print(f"{Colors.RED}Ошибка: {check_response['detail']}{Colors.ENDC}")
                    continue

            # Если пользователь существует, запрашиваем пароль
            try:
                password = curses.wrapper(getpass_with_stars)
            except:
                password = getpass_with_stars()
            
            user_data = User(login=login, password=password, token='token').model_dump_json().encode('utf-8')
            response = send_post('http://127.0.0.1:8000/auth', data=user_data)
            
            if "detail" in response:
                if "Неверный пароль" in response["detail"]:
                    print(f"{Colors.RED}Неверно введен пароль. Попробуйте снова.{Colors.ENDC}")
                    continue
                else:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            if isinstance(response, str):
                response = json.loads(response)
            user_token = response.get("token")
            return True
            
        except KeyboardInterrupt:
            print("\nОперация отменена пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла ошибка: {e}{Colors.ENDC}")
            continue


def registration():
    global user_token
    while True:
        try:
            login = input("Придумайте логин: ")
            if not login.strip():
                print(f"{Colors.RED}Ошибка: Логин не может быть пустым. Попробуйте снова.{Colors.ENDC}")
                continue

            password = get_password()
            if not password:
                continue

            user_data = User(login=login, password=password, token='token').model_dump_json().encode('utf-8')
            response = send_post('http://127.0.0.1:8000/register', data=user_data)
            
            if "detail" in response:
                if "Пользователь уже существует" in response["detail"]:
                    print(f"{Colors.YELLOW}Пользователь с таким логином уже существует. Попробуйте другой логин.{Colors.ENDC}")
                    continue
                else:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            if isinstance(response, str):
                response = json.loads(response)
            user_token = response.get("token")
            return True
            
        except KeyboardInterrupt:
            print("\nОперация отменена пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла ошибка: {e}{Colors.ENDC}")
            continue


def change_the_password():
    global user_token
    while True:
        try:
            try:
                old_password = curses.wrapper(getpass_with_stars, "Введите старый пароль: ")
            except:
                old_password = getpass_with_stars("Введите старый пароль: ")
            
            if not old_password.strip():
                print(f"{Colors.RED}Ошибка: Старый пароль не может быть пустым{Colors.ENDC}")
                continue

            password = get_password()
            if not password:
                continue

            if old_password == password:
                print(f"{Colors.YELLOW}Новый пароль совпадает со старым. Пожалуйста, введите другой пароль.{Colors.ENDC}")
                continue

            password_request = Change_Password_Request(
                old_password=old_password,
                new_password=password,
                token=user_token
            ).model_dump_json().encode('utf-8')
            
            # Сначала проверяем валидность токена
            check_token = Token(token=user_token).model_dump_json().encode('utf-8')
            check_response = send_get('http://127.0.0.1:8000/check_token', data=check_token)
            
            if "detail" in check_response:
                print(f"{Colors.RED}Ошибка: Сессия истекла. Пожалуйста, авторизуйтесь заново.{Colors.ENDC}")
                return False

            response = send_patch('http://127.0.0.1:8000/change_password', data=password_request)
            
            if "detail" in response:
                if "Неверный старый пароль" in response["detail"]:
                    print(f"{Colors.RED}Ошибка: Неверно введен старый пароль{Colors.ENDC}")
                    continue
                elif "Новый пароль не соответствует требованиям" in response["detail"]:
                    print(f"{Colors.RED}Ошибка: Новый пароль не соответствует требованиям безопасности{Colors.ENDC}")
                    continue
                else:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            new_token = response.get("token")
            if new_token:
                user_token = new_token
            return True

        except KeyboardInterrupt:
            print("\nОперация смены пароля отменена пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            return False


def add_text():
    global user_token
    while True:
        try:
            text = input("Введите текст, который хотите добавить: ")
            if not text.strip():
                print(f"{Colors.YELLOW}Предупреждение: Текст не может быть пустым. Попробуйте снова.{Colors.ENDC}")
                continue

            text_data = Text_Request(text=text, token=user_token).model_dump_json().encode('utf-8')
            response = send_post('http://127.0.0.1:8000/add_text', data=text_data)

            if "detail" in response:
                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                continue

            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            return True

        except KeyboardInterrupt:
            print("\nОперация добавления текста отменена пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            return False


def view_all():
    """Просмотр всех текстов"""
    global user_token
    while True:
        try:
            print("\nДоступные действия:")
            print("1. Просмотреть сохраненные тексты")
            print("2. Просмотреть зашифрованные тексты")
            print("3. Просмотреть расшифрованные тексты")
            print(f"{Colors.YELLOW}4. Назад{Colors.ENDC}")

            try:
                command = input("Выбор команды: ")
                if command not in ["1", "2", "3", "4"]:
                    print(f"{Colors.RED}Ошибка: Введите число от 1 до 4{Colors.ENDC}")
                    continue

                if command == "4":
                    return True

                urls = {
                    "1": "http://127.0.0.1:8000/view_all_texts",
                    "2": "http://127.0.0.1:8000/view_encrypted_texts",
                    "3": "http://127.0.0.1:8000/view_decrypted_texts"
                }

                headers = {
                    "1": "Сохраненные тексты:",
                    "2": "Зашифрованные тексты:",
                    "3": "Расшифрованные тексты:"
                }

                user = Token(token=user_token).model_dump_json().encode('utf-8')
                if not all_texts(urls[command], user, headers[command]):
                    continue
                return True

            except ValueError:
                print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                continue

        except KeyboardInterrupt:
            print("\nОперация просмотра текстов прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


def view_one_texts():
    global user_token
    while True:
        try:
            print("\nДоступные действия:")
            print("1. Просмотреть сохраненный текст")
            print("2. Просмотреть зашифрованный текст")
            print("3. Просмотреть расшифрованный текст")
            print(f"{Colors.YELLOW}4. Назад{Colors.ENDC}")

            try:
                command = input("Выбор команды: ")
                if command not in ["1", "2", "3", "4"]:
                    print(f"{Colors.RED}Ошибка: Введите число от 1 до 4{Colors.ENDC}")
                    continue

                if command == "4":
                    return True

                types = {
                    "1": ("user_text", "http://127.0.0.1:8000/view_all_texts", "Текст:"),
                    "2": ("encrypted_text", "http://127.0.0.1:8000/view_encrypted_texts", "Зашифрованный текст:"),
                    "3": ("decrypted_text", "http://127.0.0.1:8000/view_decrypted_texts", "Расшифрованный текст:")
                }

                type_name, url, header = types[command]
                user = Token(token=user_token).model_dump_json().encode('utf-8')
                response = send_get(url, data=user)
                
                if "detail" in response:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

                texts = response.get('texts', [])
                if not texts:
                    print(f"{Colors.YELLOW}Нет доступных текстов{Colors.ENDC}")
                    continue

                print("\nДоступные тексты:")
                for idx, text in enumerate(texts, 1):
                    content = text.get('content', '')
                    try:
                        content_json = json.loads(content)
                        if isinstance(content_json, dict) and 'text' in content_json:
                            content = content_json['text']
                    except (json.JSONDecodeError, TypeError):
                        pass
                    print(f"{idx}. {content}")

                while True:
                    try:
                        text_number = int(input("\nВведите номер текста (0 для отмены): ")) - 1
                        if text_number == -1:
                            break
                        if 0 <= text_number < len(texts):
                            request = One_Text_Request(
                                token=user_token,
                                text_number=text_number,
                                type=type_name
                            ).model_dump_json().encode('utf-8')

                            response = send_get('http://127.0.0.1:8000/view_one_text', data=request)
                            
                            if "detail" in response:
                                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                                break

                            print(f"\n{header}")
                            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
                            return True
                        else:
                            print(f"{Colors.RED}Ошибка: Введите число от 1 до {len(texts)}{Colors.ENDC}")
                    except ValueError:
                        print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")

            except ValueError:
                print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                continue

        except KeyboardInterrupt:
            print("\nОперация просмотра текста прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


def delete_text():
    """Удаление текста"""
    global user_token
    while True:
        try:
            print("\nДоступные действия:")
            print("1. Удалить сохраненный текст")
            print("2. Удалить зашифрованный текст")
            print("3. Удалить расшифрованный текст")
            print(f"{Colors.YELLOW}4. Назад{Colors.ENDC}")

            try:
                command = input("Выбор команды: ")
                if command not in ["1", "2", "3", "4"]:
                    print(f"{Colors.RED}Ошибка: Введите число от 1 до 4{Colors.ENDC}")
                    continue

                if command == "4":
                    return True

                types = {
                    "1": ("user_text", "http://127.0.0.1:8000/view_all_texts", "Тексты:"),
                    "2": ("encrypted_text", "http://127.0.0.1:8000/view_encrypted_texts", "Зашифрованные тексты:"),
                    "3": ("decrypted_text", "http://127.0.0.1:8000/view_decrypted_texts", "Расшифрованные тексты:")
                }

                type_name, url, header = types[command]
                user = Token(token=user_token).model_dump_json().encode('utf-8')
                texts = del_text(url, user, header)
                
                if not texts:
                    continue

                while True:
                    try:
                        text_number = int(input("\nВведите номер текста для удаления (0 для отмены): ")) - 1
                        if text_number == -1:
                            print(f"{Colors.YELLOW}Операция удаления отменена{Colors.ENDC}")
                            break
                        if 0 <= text_number < len(texts):
                            request = Delete_Request(
                                token=user_token,
                                text_number=text_number,
                                type=type_name
                            ).model_dump_json().encode('utf-8')
                            
                            response = send_delete('http://127.0.0.1:8000/delete_text', data=request)
                            
                            if "detail" in response:
                                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                                break

                            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
                            return True
                        else:
                            print(f"{Colors.RED}Ошибка: Введите число от 1 до {len(texts)}{Colors.ENDC}")
                    except ValueError:
                        print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")

            except ValueError:
                print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                continue

        except KeyboardInterrupt:
            print("\nОперация удаления текста прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


def change_the_text():
    global user_token
    while True:
        try:
            user = Token(token=user_token).model_dump_json().encode('utf-8')
            response = send_get('http://127.0.0.1:8000/view_all_texts', data=user)
            
            if "detail" in response:
                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                return False

            texts = response.get('texts', [])
            if not texts:
                print(f"{Colors.YELLOW}У вас нет текстов для изменения{Colors.ENDC}")
                return False

            print("\nДоступные тексты:")
            for index, text_info in enumerate(texts, start=1):
                print(f"{index}. {text_info['content']}")

            while True:
                try:
                    text_number = int(input("Введите номер текста для изменения (0 для отмены): "))
                    if text_number == 0:
                        print(f"{Colors.YELLOW}Операция изменения текста отменена{Colors.ENDC}")
                        return False
                        
                    if 1 <= text_number <= len(texts):
                        new_text = input("Введите новый текст: ").strip()
                        if not new_text:
                            print(f"{Colors.RED}Ошибка: Новый текст не может быть пустым{Colors.ENDC}")
                            continue

                        change_text = Change_Text_Request(
                            token=user_token,
                            text_number=text_number,
                            new_text=new_text
                        ).model_dump_json().encode('utf-8')

                        response = send_patch('http://127.0.0.1:8000/change_the_text', data=change_text)
                        
                        if "detail" in response:
                            print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                            continue

                        print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
                        return True
                    else:
                        print(f"{Colors.RED}Ошибка: Введите номер от 1 до {len(texts)}{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Ошибка: Введите корректный номер текста{Colors.ENDC}")

        except KeyboardInterrupt:
            print("\nОперация изменения текста прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            return False


def encrypt_text():
    global user_token
    while True:
        try:
            print("\nДоступные действия:")
            print("1. Выбрать текст из сохраненных")
            print("2. Ввести новый текст ")
            print(f"{Colors.YELLOW}3. Назад{Colors.ENDC}")

            try:
                command = int(input("Выбор команды: "))
                if command not in [1, 2, 3]:
                    print(f"{Colors.RED}Ошибка: Введите число от 1 до 3{Colors.ENDC}")
                    continue

                if command == 3:
                    return True

                if command == 1:
                    user = Token(token=user_token).model_dump_json().encode('utf-8')
                    text = text_selection(
                        url='http://127.0.0.1:8000/view_all_texts',
                        user=user,
                        header="Тексты:",
                        action="зашифровать"
                    )
                    if not text:
                        print(f"{Colors.YELLOW}Операция шифрования отменена{Colors.ENDC}")
                        continue
                else:
                    text = input("Введите текст для шифрования: ").strip()
                    if not text:
                        print(f"{Colors.RED}Ошибка: Текст не может быть пустым{Colors.ENDC}")
                        continue

                print("\nГенерация ключей для шифрования...")
                key = get_keys(text)

                data = Cipher_Request(
                    text=text,
                    key=key,
                    token=user_token
                ).model_dump_json().encode('utf-8')

                response = send_post('http://127.0.0.1:8000/cipher_encrypt', data=data)
                
                if "detail" in response:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

                print(f"{Colors.GREEN}Текст успешно зашифрован!{Colors.ENDC}")
                print(f"Зашифрованный текст: {response['message']}")
                return True

            except ValueError:
                print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                continue

        except KeyboardInterrupt:
            print("\nОперация шифрования прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


def decrypt_text():
    global user_token
    while True:
        try:
            print("\nДоступные действия:")
            print("1. Выбрать текст из зашифрованных")
            print(f"{Colors.YELLOW}2. Назад{Colors.ENDC}")

            try:
                command = int(input("Выбор команды: "))
                if command not in [1, 2]:
                    print(f"{Colors.RED}Ошибка: Введите 1 или 2{Colors.ENDC}")
                    continue

                if command == 2:
                    return True

                user = Token(token=user_token).model_dump_json().encode('utf-8')
                text, key = text_selection(
                    url='http://127.0.0.1:8000/view_encrypted_texts',
                    user=user, 
                    header="Зашифрованные тексты:", 
                    action="расшифровать"
                )

                if not text:
                    print(f"{Colors.YELLOW}Операция расшифровки отменена{Colors.ENDC}")
                    continue

                print(f"\n{Colors.BLUE}Выполняется расшифровка...{Colors.ENDC}")
                data = Cipher_Request(
                    text=text,
                    key=key,
                    token=user_token
                ).model_dump_json().encode('utf-8')

                response = send_post('http://127.0.0.1:8000/cipher_decrypt', data=data)
                
                if "detail" in response:
                    print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                    continue

                print(f"{Colors.GREEN}Текст успешно расшифрован!{Colors.ENDC}")
                print(f"Расшифрованный текст: {response['message']}")
                return True
            
            except ValueError:
                print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                continue

        except KeyboardInterrupt:
            print("\nОперация расшифровки прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


def query_history():
    while True:
        try:
            user = Token(token=user_token).model_dump_json().encode('utf-8')
            response = send_get('http://127.0.0.1:8000/query_history', data=user)
            
            if "detail" in response:
                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                return False

            requests = response.get('requests', [])
            if not requests:
                print(f"{Colors.YELLOW}История запросов пуста{Colors.ENDC}")
                return True

            print(f"\n{Colors.BLUE}История запросов:{Colors.ENDC}")
            for index, text_info in enumerate(requests, start=1):
                print(f"{index}. {text_info['content']}")
            return True

        except KeyboardInterrupt:
            print("\nПросмотр истории запросов прерван пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            return False


def delete_query_history():
    while True:
        try:
            confirm = input(f"{Colors.YELLOW}Вы уверены, что хотите удалить всю историю запросов? (да/нет): {Colors.ENDC}").lower()
            if confirm not in ['да', 'нет']:
                print(f"{Colors.RED}Ошибка: Введите 'да' или 'нет'{Colors.ENDC}")
                continue
                
            if confirm == 'нет':
                print(f"{Colors.YELLOW}Операция отменена{Colors.ENDC}")
                return False

            user = Token(token=user_token).model_dump_json().encode('utf-8')
            response = send_delete('http://127.0.0.1:8000/delete_query_history', data=user)
            
            if "detail" in response:
                print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
                return False

            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            return True

        except KeyboardInterrupt:
            print("\nОперация удаления истории прервана пользователем")
            return False
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            return False


def exit():
    try:
        user = Token(token=user_token).model_dump_json().encode('utf-8')
        response = send_delete('http://127.0.0.1:8000/exit', data=user)
        
        if "detail" in response:
            print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
            return False

        print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
        return True

    except Exception as e:
        print(f"{Colors.RED}Произошла ошибка при выходе: {str(e)}{Colors.ENDC}")
        return False
        

def main():
    authenticated, title, active = False, True, True
    while active:
        try:
            if title:
                print(f"\n{Colors.BLUE}Добро пожаловать!{Colors.ENDC}")
                print(f"{Colors.BLUE}Мы рады вас видеть в нашей системе 'Двойная табличная перестановка'.{Colors.ENDC}")
                title = False

            if not authenticated:
                print("\nВыберите действие:")
                print(f"{Colors.BLUE}1 - Авторизация{Colors.ENDC}")
                print(f"{Colors.GREEN}2 - Регистрация{Colors.ENDC}")
                print(f"{Colors.RED}3 - Выход{Colors.ENDC}")
                
                try:
                    command = int(input("Выбор команды: "))
                    if command not in [1, 2, 3]:
                        print(f"{Colors.RED}Ошибка: Введите число от 1 до 3{Colors.ENDC}")
                        continue

                    if command == 1:
                        authenticated = auth()
                    elif command == 2:
                        authenticated = registration()
                    else:  # command == 3
                        print(f"{Colors.YELLOW}Выход из системы.{Colors.ENDC}")
                        break

                except ValueError:
                    print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                    continue

            else:  # Меню после авторизации
                print(f"\n{Colors.BLUE}Выберите действие:{Colors.ENDC}")
                print("1 - Шифрование текста")
                print("2 - Дешифрование текста")
                print("3 - Добавить текст")
                print("4 - Просмотреть все тексты")
                print("5 - Просмотреть один текст")
                print("6 - Изменить текст")
                print("7 - Удалить текст")
                print("8 - История запросов")
                print("9 - Удалить историю запросов")
                print("10 - Изменение пароля")
                print(f"{Colors.RED}11 - Выход{Colors.ENDC}")

                try:
                    command = int(input("Выбор команды: "))
                    if command not in range(1, 12):
                        print(f"{Colors.RED}Ошибка: Введите число от 1 до 11{Colors.ENDC}")
                        continue

                    actions = {
                        1: encrypt_text,
                        2: decrypt_text,
                        3: add_text,
                        4: view_all,
                        5: view_one_texts,
                        6: change_the_text,
                        7: delete_text,
                        8: query_history,
                        9: delete_query_history,
                        10: change_the_password
                    }

                    if command == 11:
                        if exit():
                            authenticated, title = False, True
                            continue  # Возвращаемся к начальному меню
                    else:
                        actions[command]()

                except ValueError:
                    print(f"{Colors.RED}Ошибка: Введите корректное число{Colors.ENDC}")
                    continue

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Программа завершена пользователем{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}Произошла неожиданная ошибка: {str(e)}{Colors.ENDC}")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Colors.RED}Критическая ошибка: {str(e)}{Colors.ENDC}")