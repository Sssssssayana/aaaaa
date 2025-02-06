import json
from colors import Colors  # Изменить импорт


def error1(response):
    """Проверка ответа на наличие ошибок"""
    if isinstance(response, dict):
        if "detail" in response:
            print(f"{Colors.RED}Ошибка: {response['detail']}{Colors.ENDC}")
            return False
        if "message" in response and isinstance(response["message"], str):
            print(f"{Colors.GREEN}{response['message']}{Colors.ENDC}")
            return True
    return True

def error2(response):
    """Проверка ответа сервера на наличие ошибок"""
    # Если ответ уже содержит detail, пропускаем его обработку,
    # так как он будет обработан в предыдущей проверке
    if isinstance(response, dict) and "detail" in response:
        return True
        
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            print(f"{Colors.RED}Ошибка: Неверный формат ответа сервера{Colors.ENDC}")
            return False
            
    if not isinstance(response, dict):
        print(f"{Colors.RED}Ошибка: Неверный формат ответа сервера{Colors.ENDC}")
        return False
        
    if "error" in response:
        print(f"{Colors.RED}Ошибка: {response['error']}{Colors.ENDC}")
        return False
        
    return True