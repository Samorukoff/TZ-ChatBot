from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                            InlineKeyboardButton, InlineKeyboardMarkup)
import app.google_sheets as gs

# Клавиатура базовая
base = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад'), 
                                      KeyboardButton(text='Перезапуск')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите действие...')

# Клавиатура для выбора: "Прикреплять или не прикреплять изображение"
pic = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Прикрепить изображение'), 
                                      KeyboardButton(text='Изображение отсутствует')],
                                      [KeyboardButton(text='Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие...')

# Клавиатура в сообщении бота со всеми значениями name из таблицы с работниками
def create_names_keyboard():
    buttons = []
    # Для каждого значения из списка имен создаем кнопку
    for value in gs.names_of_employees():
        button = InlineKeyboardButton(text=value, callback_data=value)
        buttons.append([button])
    # Полученный список из кнопок вставляем в нашу клавиатуру
    names_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return names_keyboard

# Клавиатура завершения составления ТЗ
see_results_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Просмотреть результат'), 
                                      KeyboardButton(text='Перезапуск')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие...')

# Клавиатура проверки ТЗ
complete_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Все верно'), 
                                      KeyboardButton(text='Исправить')]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                            input_field_placeholder='Выберите действие...')

# Клавиатура в сообщении бота со всеми названиями каналов, в которые можно отправить ТЗ
def create_chats_keyboard():
    buttons = []
    # Для каждого значения из списка имен создаем кнопку
    for value in gs.chat_names():
        button = InlineKeyboardButton(text=value, callback_data=value)
        buttons.append([button])
    # Полученный список из кнопок вставляем в нашу клавиатуру
    chats_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, one_time_keyboard=True)
    return chats_keyboard