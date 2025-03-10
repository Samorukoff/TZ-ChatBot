import re

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.google_sheets as gs

# Создаем роутер для работы с диспетчером из bot.py
router = Router()

# Создаем дочерний класс по StatesGroup для создания состояний
class TechSpecific(StatesGroup):
  admin = State()
  pic = State()
  text = State()
  responsible = State()
  deadlining = State()
  see_results = State()
  complete = State()
  send = State()

@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    data = await state.get_data()
    previous_state = data.get("previous_state")
    previous_message = data.get("previous_message")
    previous_keyboard = data.get("previous_keyboard")

    if previous_state:
        await state.set_state(previous_state)
        await message.answer(previous_message, reply_markup=previous_keyboard)
    else:
        await message.answer("Ошибка: предыдущее состояние не найдено.")

# Начальный этап. Проверка на админа и выбор, есть ли изображение
@router.message(StateFilter(TechSpecific.complete), F.text=="Исправить")
@router.message(F.text=="Перезапуск")
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
  user_id = message.from_user.id
  await state.update_data(user_id = user_id)
  # Достаем ID пользователя по его сообщению, проверяем, есть ли он в списке админов
  if str(user_id) in gs.checking_for_an_admin():
    await message.answer('Приветствуем вас, администратор, давайте начнем составлять ТЗ. '
    'Выберите соответствующий пункт в зависимости от наличия изображения к ТЗ.', reply_markup=kb.pic)
    await state.set_state(TechSpecific.admin)
  elif str(user_id) not in gs.checking_for_an_admin():
    await message.answer('Приветствуем вас, пользователь, к сожалению, у вас нет прав для составления ТЗ')

  else: await message.answer('Произошла ошибка')

# Обработчик сообщения 'Изображение отсутствует'
@router.message(StateFilter(TechSpecific.admin), F.text =='Изображение отсутствует')
async def cmd_pic(message: Message, state: FSMContext):
  file_id = "Отсутствует"
  # Записываем результат и прошлые состояния
  await state.update_data(file_id=file_id,
    previous_state=await state.get_state(),
    previous_message='Приветствуем вас, администратор, давайте начнем составлять ТЗ.'
    ' Выберите соответствующий пункт в зависимости от наличия изображения к ТЗ.',
    previous_keyboard=kb.pic)
  # Переходим к состоянию ожидания ввода текста ТЗ
  await state.set_state(TechSpecific.text)
  await message.answer('Оставьте текст технического задания:', reply_markup=kb.base)

# Обработчик сообщения 'Прикрепить изображение'
@router.message(StateFilter(TechSpecific.admin), F.text =='Прикрепить изображение')
async def cmd_pic(message: Message, state: FSMContext):
  # Записываем прошлые состояния
  await state.update_data(previous_state=await state.get_state(),
    previous_message='Приветствуем вас, администратор, давайте начнем составлять ТЗ.'
    ' Выберите соответствующий пункт в зависимости от наличия изображения к ТЗ.',
    previous_keyboard=kb.pic)
  # Переходим к состоянию ожидания изображения
  await state.set_state(TechSpecific.pic)
  await message.answer('Прикрепите ваше изображение:', reply_markup=kb.base)

# Обработчик полученного фото
@router.message(TechSpecific.pic)
async def cmd_pic_save(message: Message, state: FSMContext):
  try:
    # Достаем ID фото
    file_id = message.photo[-1].file_id
    # Записываем результат и прошлые состояния
    await state.update_data(file_id=file_id,
      previous_state=await state.get_state(),
      previous_message='Прикрепите ваше изображение:')
    # Переходим к состоянию ожидания ввода текста ТЗ
    await state.set_state(TechSpecific.text)
    await message.answer("Введите текст технического задания:")
  except TypeError:
    await message.answer("Сообщение не соответствует требуемому формату")

# Обработчик полученного текста
@router.message(TechSpecific.text)
async def names_inline_keyboard(message: Message, state: FSMContext):
  try:
    # Записываем результат и прошлые состояния
    text = message.text
    await state.update_data(text=text,
      previous_state=await state.get_state(),
      previous_message='Введите текст технического задания:')
    # Переходим к состоянию ожидания выбора ответственного
    await state.set_state(TechSpecific.responsible)
    # Вызываем клавиатуру-список работников для выбора
    names_keyboard = kb.create_names_keyboard()
    await message.answer("Теперь выберите ответственного:", reply_markup=names_keyboard)
  except TypeError:
    await message.answer("Сообщение не соответствует требуемому формату")

# Обработчик результата нажатия кнопки в списке ответственных
@router.callback_query(TechSpecific.responsible)
async def responsible_guy(callback: CallbackQuery, state: FSMContext):
  # Получаем результат, записываем его вместе с прошлыми состояниями
  responsible = str(callback.data)
  await state.update_data(responsible=responsible,
      previous_state=await state.get_state(),
      previous_message='Теперь выберите ответственного:',
      previous_keyboard=kb.create_names_keyboard())
  # Переходим к состоянию выбора дедлайна
  await state.set_state(TechSpecific.deadlining)
  await callback.answer(f"Ответственный за ТЗ: {responsible}")
  await callback.message.answer("Пожалуйста, введите дату крайнего срока выполнения задания в формате ДД.ММ.ГГ",
                                reply_markup=kb.base)

# Обработчик введенной даты
@router.message(TechSpecific.deadlining)
async def deadline(message: Message, state: FSMContext):
  try:
    # На всявкий случай удаляем пробелы
    deadline_date = message.text.strip()
    # Проверка даты на соответствие формату
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{2}", deadline_date):
      await message.answer("Дата введена в неверном формате, используйте формат ДД.ММ.ГГ")
    else:
      # Записываем
      await state.update_data(deadline_date=deadline_date,
        previous_state=await state.get_state(),
        previous_message='Пожалуйста, введите дату крайнего срока выполнения задания в формате ДД.ММ.ГГ',
        previous_keyboard=kb.base)
      # Переходим в состояние показа результата
      await state.set_state(TechSpecific.see_results)
      await message.answer("Ваше ТЗ составлено", reply_markup=kb.see_results_keyboard)
  except TypeError:
    await message.answer("Сообщение не соответствует требуемому формату")

# Обработчик, выводящий весь результат составления ТЗ
@router.message(StateFilter(TechSpecific.see_results), F.text == "Просмотреть результат")
async def checking(message: Message, state: FSMContext, bot: Bot):
  # Достаем все данные
  await message.answer("Составленное ТЗ:")
  data = await state.get_data()
  file_id = str(data.get("file_id"))
  text = str(data.get("text"))
  responsible = str(data.get("responsible"))
  deadline_date = data.get("deadline_date")
  # Учитываем возможность отсутствия изображения
  if file_id != "Отсутствует":
    await bot.send_photo(chat_id=message.chat.id, photo=file_id)
  else: pass
  # Демонстрация результата, все выводим
  await message.answer(text)
  await message.answer(f"Ответственный за выполнение ТЗ: {responsible}")
  await message.answer(f"Срок сдачи: {deadline_date}г.", reply_markup=kb.complete_keyboard)
  # Переходим в состояние подтверждения результата
  await state.set_state(TechSpecific.complete)

#Обработчик подтверждения результата, вывод меню выбора чата для отправки
@router.message(StateFilter(TechSpecific.complete), F.text == "Все верно")
async def complete(message: Message, state: FSMContext):
  # Достаем все записанные ранее переменные
  data = await state.get_data()
  file_id = data.get("file_id")
  user_id = data.get("user_id")
  responsible = data.get("responsible")
  text = data.get("text")
  deadline_date = data.get("deadline_date")
  # Вызываем функцию записи, заполняем таблицу GoogleSheets
  gs.writing(file_id, user_id, text, responsible, deadline_date)
  # Переходим в состояние отправки ТЗ в чат
  await state.set_state(TechSpecific.send)
  # Вызываем собранную клавиатуру
  chats_keyboard = kb.create_chats_keyboard()
  await message.answer("Техническое задание готово! Выберите, в какой канал его отправить:",
                       reply_markup=chats_keyboard)

# Обработчик выбранного чата, отправка
@router.callback_query(TechSpecific.send)
async def sending_to_chat(callback: CallbackQuery, state: FSMContext, bot: Bot):
  # Достаем из таблицы соответствующий названию ID чата
  chat_name = callback.data
  chat_id = gs.get_chat_id_by_name(chat_name)
  # Достаем все составляющие ТЗ
  data = await state.get_data()
  file_id = data.get("file_id")
  responsible = data.get("responsible")
  text = data.get("text")
  deadline_date = data.get("deadline_date")
  # Отправляем все в выбранный чат
  await bot.send_message(chat_id=chat_id, text=f"Техническое задание")
  await bot.send_photo(chat_id=chat_id, photo=file_id)
  await bot.send_message(chat_id=chat_id, text=text)
  await bot.send_message(chat_id=chat_id, text=f"Ответственный: {responsible}")
  await bot.send_message(chat_id=chat_id, text=f"Срок сдачи: {deadline_date}")
  await callback.answer(f'ТЗ отправлено в "{chat_name}"', show_alert=True)
  # Завершение цикла создания ТЗ
  await callback.message.answer('Чтобы создать другое ТЗ, нажмите "Перезапуск"', reply_markup=kb.base)
  # Очистка состояний
  await state.clear()
