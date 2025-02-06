from pydantic import BaseModel
from typing import Union, List

class User(BaseModel): #модель для пользователя
    login: str
    password: str
    token: str = None  
    id: Union[int, None] = None

class Change_Text_Request(BaseModel): #модель для изменения текста
    token: str
    text_number: int
    new_text: str 

class Delete_Request(BaseModel): #модель для удаления текста
    token: str
    text_number: int
    type: str

class One_Text_Request(BaseModel): #модель для просмотра одного текста
    token: str
    text_number: int
    type: str

class Cipher_Request(BaseModel):
    """Модель для шифрования/дешифрования методом двойной табличной перестановки"""
    text: str
    key: List[int]  # Первая половина - перестановка столбцов, вторая - строк
    token: str

class Change_Password_Request(BaseModel): #модель для смены пароля
    old_password: str
    new_password: str
    token: str

class Text_Request(BaseModel): #модель для работы с текстом
    text: str
    token: str

class Token(BaseModel):
    token: str

class EncryptedText(BaseModel):
    """Модель для хранения зашифрованного текста с ключами"""
    text: str
    col_key: List[int]  # ключ для столбцов
    row_key: List[int]  # ключ для строк