import time, json, os

def token_search(token: str): # поиск пользователя по токену
    file_path = 'users'
    user_id = None
    user_login = None
    for json_file in os.listdir(file_path):
        if json_file.endswith('.json'):
            file1_path = os.path.join(file_path, json_file)
            with open(file1_path, 'r', encoding="utf-8") as f:
                tmp_user = json.load(f)
            if tmp_user['token'] == token:
                user_id = tmp_user['id']
                user_login = tmp_user['login']
                return user_id, user_login
    return None

def login_search(login: str, folder_path: str = 'users') -> dict: #поиск пользователя по логину
    for json_file in os.listdir(folder_path):
        if json_file.endswith('.json'):
            file_path = os.path.join(folder_path, json_file)
            with open(file_path, 'r') as f:
                tmp_user = json.load(f)
                if tmp_user['login'] == login:
                    return tmp_user
    return None

def request(user_id: str, user_login: str, action: str): #для записи запросов, которые выполняются
    folder_path = 'query_history'
    os.makedirs(folder_path, exist_ok=True)
    user_folder = os.path.join(folder_path, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    current_time = int(time.time())
    file_name = f"request_{current_time}.txt"
    file_path = os.path.join(user_folder, file_name)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"Время: {timestamp} Пользователь:{user_login} Действие: {action}\n")