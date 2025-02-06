import urllib.request
import json
from colors import Colors

def send_post(url, data):
    request = urllib.request.Request(url, data=data, method='POST')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        try:
            error_data = json.loads(error_message)
            return {"detail": error_data.get("detail", "Ошибка запроса")}
        except json.JSONDecodeError:
            return {"detail": "Ошибка при обработке ответа сервера"}
    except Exception as e:
        return {"detail": f"Ошибка сети: {str(e)}"}

def send_get(url, data):
    request = urllib.request.Request(url, data=data, method='GET')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        try:
            error_data = json.loads(error_message)
            if e.code == 401:
                return {"detail": "Сессия истекла. Пожалуйста, авторизуйтесь заново."}
            return {"detail": error_data.get("detail", "Ошибка запроса")}
        except json.JSONDecodeError:
            return {"detail": "Ошибка при обработке ответа сервера"}
    except Exception as e:
        return {"detail": f"Ошибка сети: {str(e)}"}

def send_patch(url, data):
    request = urllib.request.Request(url, data=data, method='PATCH')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        try:
            error_data = json.loads(error_message)
            return {"detail": error_data.get("detail", "Ошибка запроса")}
        except json.JSONDecodeError:
            return {"detail": "Ошибка при обработке ответа сервера"}
    except Exception as e:
        return {"detail": f"Ошибка сети: {str(e)}"}

def send_delete(url, data):
    request = urllib.request.Request(url, data=data, method='DELETE')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        try:
            error_data = json.loads(error_message)
            return {"detail": error_data.get("detail", "Ошибка запроса")}
        except json.JSONDecodeError:
            return {"detail": "Ошибка при обработке ответа сервера"}
    except Exception as e:
        return {"detail": f"Ошибка сети: {str(e)}"}