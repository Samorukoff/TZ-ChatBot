import os
from dotenv import load_dotenv 

import gspread
from google.oauth2.service_account import Credentials

# Загружаем переменные окружения
load_dotenv()

# Функция подключения к Google API и получение списка ID администраторов
def checking_for_an_admin():
    try:
        # Определяем область доступа, проводим аутентификацию, создаем клиент Google Sheets API
        creds = Credentials.from_service_account_file(os.getenv("CREDENTIALS", "app/credentials.json"),
                                                      scopes=["https://www.googleapis.com/auth/spreadsheets"])
        
        client = gspread.authorize(creds)
        # Выбираем нужную книгу
        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)

        # Достаем список ID администраторов
        administrators = workbook.worksheet("Administrators")
        admin_id_list = administrators.col_values(1)[1:]
        return (admin_id_list)
        
    except Exception as e:
        print(f"Ошибка при получении списка администраторов из Google Sheets: {e}")
        return []

# Функция подключения к Google API и получение списка имен работников
def names_of_employees():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("app/credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)

        # Достаем список имен работников
        employees = workbook.worksheet("Employees")
        name_list = employees.col_values(2)[1:]
        return name_list

    except Exception as e:
        print(f"Ошибка при получении списка в Google Sheets: {e}")
        return []

# Функция подключения к Google API и получение списка названий чатов
def chat_names():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("app/credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)

        # Достаем список названий каналов
        chats = workbook.worksheet("Chats")
        chat_names_list = chats.col_values(2)[1:]
        return chat_names_list
    except Exception as e:
        print(f"Ошибка при получении списка в Google Sheets: {e}")
        return []
    
# Функция для получения ID чата по его названию из Google Sheets
def get_chat_id_by_name(chat_name: str):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("app/credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)

        # Достаем списки названий каналов и соответствующих ID
        chats = workbook.worksheet("Chats")
        chat_names_list = chats.col_values(2)[1:]
        chat_id_list = chats.col_values(1)[1:]

        # Создаем словарь для соответствия названия и ID
        chat_dictionary = dict(zip(chat_names_list, chat_id_list))

        # Возвращаем ID по названию
        return chat_dictionary.get(chat_name)
    except Exception as e:
        print(f"Ошибка при получении ID чата из Google Sheets: {e}")
        return None

# Функция для получения 
def get_chat_id_by_name(chat_name: str):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("app/credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)

        # Достаем списки названий каналов и соответствующих ID
        chats = workbook.worksheet("Chats")
        chat_names_list = chats.col_values(2)[1:]
        chat_id_list = chats.col_values(1)[1:]

        # Создаем словарь для соответствия названия и ID
        chat_dictionary = dict(zip(chat_names_list, chat_id_list))

        # Возвращаем ID по названию
        return chat_dictionary.get(chat_name)
    except Exception as e:
        print(f"Ошибка при получении ID чата из Google Sheets: {e}")
        return None

# Функция подключения к Google API и внесения данных в таблицу Google Sheets
def writing(file_id, user_id, text, responsible_id, deadline_date):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("app/credentials.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1l6L6NOjRruRjmvgv-tYqATkduQ4SXp4AE6pfpeTGKkA"
        workbook = client.open_by_key(sheet_id)
        tech_specific = workbook.worksheet("TechSpecific")

        # Вписываем значения в одну строку по порядку
        tech_specific.append_row([user_id, file_id, text, responsible_id, deadline_date])
        return True

    except Exception as e:
        print(f"Ошибка при записи данных в Google Sheets: {e}")
        return False