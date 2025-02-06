from fastapi import FastAPI, HTTPException
import time, json, os, hashlib, secrets  # для хеширования пароля и токена
from models import Change_Text_Request, Delete_Request, One_Text_Request, Cipher_Request, User, Change_Password_Request, \
    Text_Request, Token
from text_fun import gronsfeld_encrypt, gronsfeld_decrypt
from password_veri import complex_password_s
from addit import token_search, login_search, request

app = FastAPI()


@app.post("/register")  # регистрация пользователя
def create_user(user: User):
    if not user.login:
        raise HTTPException(status_code=409, detail="Логин не может быть пустым")
    if not complex_password_s(user.password):
        raise HTTPException(status_code=409, detail="Пароль должен содержать минимум 8 символов, буквы, цифры и специальные символы")
    
    folder_path = 'users'
    os.makedirs(folder_path, exist_ok=True)
    if login_search(user.login, folder_path):
        raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")
    
    user.id = int(time.time())
    user.token = secrets.token_hex(8)  # генерация технического токена
    user.password = hashlib.sha256(user.password.encode()).hexdigest()  # хеширование пароля
    with open(f"users/user_{user.id}.json", 'w') as f:  # сохранение пользователя
        json.dump(user.dict(), f)
    request(user.id, user.login, f"Регистрация пользователя")  # сохранение запроса
    return {"message": "Регистрация успешна!", "token": user.token}


@app.post("/auth")  # авторизация пользователя
def authorization(user: User):
    folder_path = 'users'
    tmp_user = login_search(user.login, folder_path)
    if not tmp_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if tmp_user['password'] != hashed_password:
        raise HTTPException(status_code=401, detail="Неверный пароль")
        
    request(tmp_user['id'], tmp_user['login'], f"Авторизация пользователя")  # сохранение запроса
    return {"message": "Авторизация успешна!", "token": tmp_user['token']}


@app.patch("/change_password")
def change_the_password(data: Change_Password_Request):
    folder_path = 'users'
    user_found = False
    for json_file in os.listdir(folder_path):
        if json_file.endswith('.json'):
            file_path = os.path.join(folder_path, json_file)
            with open(file_path, 'r') as f:
                tmp_user = json.load(f)
            if tmp_user['token'] == data.token:
                user_found = True
                if tmp_user['password'] != hashlib.sha256(data.old_password.encode()).hexdigest():
                    raise HTTPException(status_code=401, detail="Неверный старый пароль")
                if not complex_password_s(data.new_password):
                    raise HTTPException(status_code=400,
                                        detail="Новый пароль не соответствует требованиям безопасности")
                tmp_user['password'] = hashlib.sha256(data.new_password.encode()).hexdigest()
                new_token = secrets.token_hex(8)
                tmp_user['token'] = new_token
                with open(file_path, 'w') as fw:
                    json.dump(tmp_user, fw)
                return {"message": "Пароль успешно изменён", "token": new_token}
    if not user_found:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.post("/add_text")  # добавление текста
def add_text2(text: Text_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'user_text'  # проверка и создание папки для текстов
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    current_time = int(time.time())
    file_name = f"text_{current_time}.txt"
    file_path = os.path.join(user_folder, file_name)  # добавление текста в файл
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text.text)
    request(user_id, user_login, f"Добавление текста")  # сохранение запроса
    return {"message": "Текст успешно добавлен!"}


@app.get("/view_all_texts")  # просмотр всех текстов пользователя
def view_all_texts(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'user_text'
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    if not os.path.exists(user_folder):  # проверка на существование папки и наличие файлов
        request(user_id, user_login, f"Просмотр всех сохраненных текстов")  # сохранение запроса
        raise HTTPException(status_code=404, detail="Нет текстов пользователя")
    if not os.listdir(user_folder):  # если папка существует, но пуста
        request(user_id, user_login, f"Просмотр всех сохраненных текстов")  # сохранение запроса
        return {"message": "У вас нет сохраненных текстов."}

    all_texts = []
    for file_name in os.listdir(user_folder):  # чтение текстов из папки пользователя
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            all_texts.append({"content": content})
    request(user_id, user_login, f"Просмотр всех сохраненных текстов")  # сохранение запроса
    return {"texts": all_texts}


@app.get("/view_encrypted_texts")
def view_encrypted_text(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'encrypted_text'
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    if not os.path.exists(user_folder):
        request(user_id, user_login, f"Просмотр всех зашифрованных текстов")
        raise HTTPException(status_code=404, detail="Нет текстов для пользователя")
    if not os.listdir(user_folder):
        request(user_id, user_login, f"Просмотр всех зашифрованных текстов")
        return {"message": "У вас нет зашифрованных текстов."}

    encrypted_texts = []
    for file_name in os.listdir(user_folder):
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'r', encoding="utf-8") as file:
            if file_name.endswith('.json'):
                # Для JSON файлов читаем структурированные данные
                content = json.load(file)
                encrypted_texts.append({"content": json.dumps(content)})
            else:
                # Для обычных текстовых файлов читаем как есть
                content = file.read()
                encrypted_texts.append({"content": content})

    request(user_id, user_login, f"Просмотр всех зашифрованных текстов")
    return {"texts": encrypted_texts}


@app.get("/view_decrypted_texts")  # просмотра расшифрованных текстов пользователя
def view_decrypted_text(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'decrypted_text'
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    if not os.path.exists(user_folder):  # проверка на существование папки и наличие файлов
        request(user_id, user_login, f"Просмотр всех расшифрованных текстов")  # сохранение запроса
        raise HTTPException(status_code=404,
                            detail="Нет текстов для пользователя")  # НУЖНО ИЗМЕНИТЬ НАДПИСИ НА БОЛЕЕ КОРРЕКТНЫЕ
    if not os.listdir(user_folder):  # если папка существует, но пуста
        request(user_id, user_login, f"Просмотр всех расшифрованных текстов")  # сохранение запроса
        return {"message": "У вас нет расшифрованных текстов."}
    decrypted_texts = []
    for file_name in os.listdir(user_folder):  # чтение текстов из папки пользователя
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            decrypted_texts.append({"content": content})
    request(user_id, user_login, f"Просмотр всех расшифрованных текстов")  # сохранение запроса
    return {"texts": decrypted_texts}


@app.get("/view_one_text")
def view_one_text(text: One_Text_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    folder_path = text.type
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    if not os.path.exists(user_folder):
        request(user_id, user_login, f"Просмотр одного текста")
        raise HTTPException(status_code=404, detail="Нет текстов для пользователя")

    files = os.listdir(user_folder)
    if not files:
        request(user_id, user_login, f"Просмотр одного текста")
        return {"message": "У вас нет текстов."}

    if text.text_number < 0 or text.text_number >= len(files):
        raise HTTPException(status_code=404, detail="Текст с указанным номером не найден")

    file_path = os.path.join(user_folder, files[text.text_number])
    with open(file_path, 'r', encoding="utf-8") as f:
        content = f.read()
        try:
            # Пробуем распарсить JSON для зашифрованных текстов
            content_json = json.loads(content)
            if isinstance(content_json, dict) and 'text' in content_json:
                content = content_json['text']
        except json.JSONDecodeError:
            pass

    request(user_id, user_login, f"Просмотр одного текста")
    return {"message": content}


@app.delete("/delete_text")  # удаление текста
def delete_text(text: Delete_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_folder = os.path.join(text.type, str(user_id))
    if not os.path.exists(user_folder):  # Проверка на существование папки
        request(user_id, user_login, f"Удаление текста")  # сохранение запроса
        raise HTTPException(status_code=404, detail="Нет текстов для пользователя")
    if not os.listdir(user_folder):  # если папка существует, но пуста
        request(user_id, user_login, f"Просмотр одного текста")  # сохранение запроса
        return {"message": "У вас нет текстов для удаления."}
    files = os.listdir(user_folder)
    if text.text_number < 0 or text.text_number > len(files):
        raise HTTPException(status_code=404, detail="Текст с указанным номером не найден")
    file_to_delete = os.path.join(user_folder, files[text.text_number])  # удаление выбранного файла
    os.remove(file_to_delete)
    request(user_id, user_login, f"Удаление текста")  # сохранение запроса
    return {"message": "Текст успешно удалён"}


@app.patch("/change_the_text")  # изменение текста
def change_the_text(text: Change_Text_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_folder = os.path.join('user_text', str(user_id))  # получение списка файлов пользователя
    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        request(user_id, user_login, f"Изменение текста")  # сохранение запроса
        raise HTTPException(status_code=404, detail="Нет доступных текстов для изменения")
    files = os.listdir(user_folder)
    if text.text_number < 1 or text.text_number > len(files):
        raise HTTPException(status_code=404, detail="Текст с указанным номером не найден")
    if not text.new_text.strip():
        raise HTTPException(status_code=400, detail="Новый текст не может быть пустым")
    file_to_update = os.path.join(user_folder, files[text.text_number - 1])
    with open(file_to_update, 'w', encoding="utf-8") as f:  # обновление текста в файле
        f.write(text.new_text)
    request(user_id, user_login, f"Изменение текста")  # сохранение запроса
    return {"message": "Текст успешно обновлён"}


@app.post("/cipher_encrypt")
def encrypt(data: Cipher_Request):
    user_id, user_login = token_search(data.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        encrypted_text = gronsfeld_encrypt(data.text, data.key)
        # Разделяем ключ на две части
        cols = len(data.key) // 2
        col_key = data.key[:cols]
        row_key = data.key[cols:]

        folder_path = "encrypted_text"
        os.makedirs(folder_path, exist_ok=True)
        user_folder = os.path.join(folder_path, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        text_id = int(time.time())

        # Сохраняем зашифрованный текст и ключи в JSON
        encrypted_data = {
            "text": encrypted_text,
            "col_key": col_key,
            "row_key": row_key
        }

        file_path = os.path.join(user_folder, f"text_{text_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted_data, f)

        request(user_id, user_login, f"Шифрование текста методом двойной табличной перестановки")
        return {"message": encrypted_text, "col_key": col_key, "row_key": row_key}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/cipher_decrypt")
def decrypt(data: Cipher_Request):
    user_id, user_login = token_search(data.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        # Получаем сохраненные ключи для выбранного текста
        folder_path = "encrypted_text"
        user_folder = os.path.join(folder_path, str(user_id))

        # Находим файл с зашифрованным текстом
        for filename in os.listdir(user_folder):
            if filename.endswith('.json'):
                with open(os.path.join(user_folder, filename), 'r') as f:
                    saved_data = json.load(f)
                    if saved_data["text"] == data.text:
                        # Используем сохраненные ключи для дешифрования
                        key = saved_data["col_key"] + saved_data["row_key"]
                        decrypted_text = gronsfeld_decrypt(data.text, key)

                        # Сохраняем расшифрованный текст
                        decrypted_folder = os.path.join("decrypted_text", str(user_id))
                        os.makedirs(decrypted_folder, exist_ok=True)
                        text_id = int(time.time())
                        file_path = os.path.join(decrypted_folder, f"text_{text_id}.txt")

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(decrypted_text)

                        request(user_id, user_login, f"Дешифрование текста методом двойной табличной перестановки")
                        return {"message": decrypted_text}

        raise HTTPException(status_code=404, detail="Не найден зашифрованный текст с сохраненными ключами")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/query_history")  # просмотр истории запросов пользователя
def view_query_history(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'query_history'
    os.makedirs(folder_path, exist_ok=True)
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    if not os.path.exists(user_folder):  # проверка на существование папки и наличие файлов
        request(user_id, user_login, f"История запросов пользователя")  # сохранение запроса
        raise HTTPException(status_code=404, detail="Нет запросов пользователя")
    if not os.listdir(user_folder):  # если папка существует, но пуста
        request(user_id, user_login, f"История запросов пользователя")  # сохранение запроса
        return {"message": "У вас нет истории запросов ."}
    requests = []
    for file_name in os.listdir(user_folder):  # чтение текстов из папки пользователя
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            requests.append({"content": content})
    request(user_id, user_login, f"История запросов пользователя")  # сохранение запроса
    return {"requests": requests}


@app.delete("/delete_query_history")  # удаление истории запросов
def delete_query_history(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    folder_path = 'query_history'
    os.makedirs(folder_path, exist_ok=True)
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(folder_path, exist_ok=True)
    if not os.path.exists(user_folder):
        request(user_id, user_login, f"Удаление истории запросов пользователя")  # сохранение запрос
        raise HTTPException(status_code=404, detail="Нет истории запросов пользователя")
    for file_name in os.listdir(user_folder):
        file_path = os.path.join(user_folder, file_name)
        os.remove(file_path)
    request(user_id, user_login, f"Удаление истории запросов пользователя")  # сохранение запроса
    return {"message": "История запросов успешно удалена."}


@app.delete("/exit")  # выход из программы
def exit(data: Token):
    user_id, user_login = token_search(data.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    request(user_id, user_login, f"Выход из программы")  # сохранение запроса
    return {"message": "До новых встреч!\n"}


@app.get("/check_user")
def check_user(user: User):
    """Проверка существования пользователя по логину"""
    folder_path = 'users'
    tmp_user = login_search(user.login, folder_path)
    if not tmp_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Пользователь найден"}


@app.get("/check_token")
def check_token(token: Token):
    """Проверка валидности токена"""
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    return {"message": "Токен действителен"}