import unittest
import requests
import json
from colors import Colors

class Test1(unittest.TestCase):
    def test_register(self):
        self.login = "User1"
        self.password = "Password12345.."
        data = json.dumps({"login": self.login, "password": self.password, "token": 'token'}).encode('utf-8')
        try:
            response = requests.post("http://127.0.0.1:8000/register", data=data)
        except requests.exceptions.RequestException as e:
            self.fail(f"Ошибка при отправке запроса: {e}")
        response_json = response.json()
        self.token = response_json.get("token")
        print()
        print(response.json().get("message"))

class Test2(unittest.TestCase):
    def test_auth(self):
        self.login = "User2"
        self.password = "Password12345.."
        data = json.dumps({"login": self.login, "password": self.password, "token": 'token'}).encode('utf-8')
        response = requests.post("http://127.0.0.1:8000/register", data=data)
        response_json = response.json()
        self.token = response_json.get("token")
        data = json.dumps({"login": self.login, "password": self.password, "token": self.token}).encode('utf-8')
        try:
            response = requests.post("http://127.0.0.1:8000/auth", data=data)
        except requests.exceptions.RequestException as e:
            self.fail(f"Ошибка при отправке запроса: {e}")
        print()
        print(response.json().get("message"))

class Test3(unittest.TestCase):
    def test_encrypt_text(self):
        self.login = "User2"
        self.password = "Password12345.."
        data = json.dumps({"login": self.login, "password": self.password, "token": 'token'}).encode('utf-8')
        response = requests.post("http://127.0.0.1:8000/auth", data=data)
        response_json = response.json()
        self.token = response_json.get("token")
        self.text = "Hello World!"
        # Ключи для матрицы 3x4: [2,1,3] для столбцов и [2,1,3,4] для строк
        self.key = [2,1,3, 2,1,3,4]
        data = json.dumps({"text": self.text, "key": self.key, "token": self.token}).encode('utf-8')
        try:
            response = requests.post("http://127.0.0.1:8000/cipher_encrypt", data=data)
        except requests.exceptions.RequestException as e:
            self.fail(f"Ошибка при отправке запроса: {e}")
        print("\nИсходный текст:", self.text)
        print("Зашифрованный текст:", response.json().get("message"))

class Test4(unittest.TestCase):
    def test_decrypt_text(self):
        self.login = "User2"
        self.password = "Password12345.."
        data = json.dumps({"login": self.login, "password": self.password, "token": 'token'}).encode('utf-8')
        response = requests.post("http://127.0.0.1:8000/auth", data=data)
        response_json = response.json()
        self.token = response_json.get("token")
        # Зашифрованный текст и ключи должны соответствовать использованным при шифровании
        self.text = "el HWrdlo!ol "
        self.key = [2,1,3, 2,1,3,4]
        data = json.dumps({"text": self.text, "key": self.key, "token": self.token}).encode('utf-8')
        try:
            response = requests.post("http://127.0.0.1:8000/cipher_decrypt", data=data)
        except requests.exceptions.RequestException as e:
            self.fail(f"Ошибка при отправке запроса: {e}")
        print("\nЗашифрованный текст:", self.text)
        print("Расшифрованный текст:", response.json().get("message"))

class Test5(unittest.TestCase):
    def test_change_password(self):
        self.login = "User2"
        self.password = "Password12345.."
        data = json.dumps({"login": self.login, "password": self.password, "token": 'token'}).encode('utf-8')
        response = requests.post("http://127.0.0.1:8000/auth", data=data)
        response_json = response.json()
        self.token = response_json.get("token")
        self.password1 = "testpassword735\."
        data = json.dumps({"old_password": self.password, "new_password": self.password1, "token": self.token}).encode('utf-8')
        try:
            response = requests.patch("http://127.0.0.1:8000/change_password", data=data)
        except requests.exceptions.RequestException as e:
            self.fail(f"Ошибка при отправке запроса: {e}")
        print()
        print(response.json().get("message"))

class TestAuth(unittest.TestCase):
    def setUp(self):
        """Подготовка данных для тестов"""
        self.base_url = "http://127.0.0.1:8000"
        self.test_user = {
            "login": "test_user",
            "password": "Test123!@#",
            "token": "token"
        }
        
        # Регистрируем тестового пользователя
        try:
            response = requests.post(
                f"{self.base_url}/register",
                data=json.dumps(self.test_user).encode('utf-8')
            )
            if response.status_code == 200:
                print(f"{Colors.GREEN}Тестовый пользователь создан успешно{Colors.ENDC}")
            self.token = response.json().get("token")
        except Exception as e:
            print(f"{Colors.RED}Ошибка при создании тестового пользователя: {e}{Colors.ENDC}")

    def test_check_user_exists(self):
        """Тест проверки существующего пользователя"""
        response = requests.get(
            f"{self.base_url}/check_user",
            data=json.dumps(self.test_user).encode('utf-8')
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Пользователь найден")
        print(f"{Colors.GREEN}Тест проверки существующего пользователя пройден{Colors.ENDC}")

    def test_check_user_not_exists(self):
        """Тест проверки несуществующего пользователя"""
        non_existent_user = {
            "login": "non_existent",
            "password": "temp",
            "token": "token"
        }
        response = requests.get(
            f"{self.base_url}/check_user",
            data=json.dumps(non_existent_user).encode('utf-8')
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Пользователь не найден")
        print(f"{Colors.GREEN}Тест проверки несуществующего пользователя пройден{Colors.ENDC}")

    def test_auth_success(self):
        """Тест успешной авторизации"""
        response = requests.post(
            f"{self.base_url}/auth",
            data=json.dumps(self.test_user).encode('utf-8')
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())
        print(f"{Colors.GREEN}Тест успешной авторизации пройден{Colors.ENDC}")

    def test_auth_wrong_password(self):
        """Тест авторизации с неверным паролем"""
        wrong_pass_user = self.test_user.copy()
        wrong_pass_user["password"] = "WrongPass123!@#"
        response = requests.post(
            f"{self.base_url}/auth",
            data=json.dumps(wrong_pass_user).encode('utf-8')
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Неверный пароль")
        print(f"{Colors.GREEN}Тест авторизации с неверным паролем пройден{Colors.ENDC}")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'token'):
            # Можно добавить удаление тестового пользователя
            pass

if __name__ == "__main__":
    unittest.main()