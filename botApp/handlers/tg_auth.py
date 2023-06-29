from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from werkzeug.security import check_password_hash
from manage import app
from botApp.create_bot import bot

from app.util import dbase


class Booking(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


async def tg_auth(message: types.Message, state: FSMContext):
    await state.finish()
    with app.app_context():
        if dbase.check_tg_auth(message.chat.id) == 0:
            types.reply_markup = types.ReplyKeyboardRemove()
            await message.answer("Авторизируйтесь для работы с приложением. \nВведите ваш логин")
            await Booking.waiting_for_login.set()
        else:
            types.reply_markup = types.ReplyKeyboardRemove()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Сменить пользователя']
            keyboard.add(*buttons)
            await message.answer("Вы уже авторизованы", reply_markup=keyboard)


async def tg_insert_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await Booking.waiting_for_password.set()
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1, text='Введите ваш пароль')


async def tg_insert_pass(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        with app.app_context():
            user = dbase.getUserByLogin(data['login'])
            if user and check_password_hash(user.psw, message.text):
                print(dbase.get_role(user.role))
                if dbase.get_role(user.role) == "tender":
                    dbase.tg_login(data['login'], message.chat.id)
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    buttons = ['Сменить пользователя']
                    keyboard.add(*buttons)
                    await message.answer(
                        "Вы успешно авторизовались! "
                        "Теперь вы будете получать уведомление и нахождении новых подходящих заявках.",
                        reply_markup=keyboard)
                    await state.finish()
                else:
                    await message.answer("Работа для вашей роли временно не определена. Попробуйте позже")
                    await state.finish()
            else:
                await message.answer("Некорректный логин или пароль")
                await state.finish()
                await message.answer("Введите ваш логин")
                await Booking.waiting_for_login.set()
    await delete_messages(message)


async def tg_logout(message: types.Message, state: FSMContext):
    with app.app_context():
        dbase.tg_logout(message.chat.id)
    types.reply_markup = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer("Вы вышли из аккаунта. Для авторизации введите ваш логин")
    await Booking.waiting_for_login.set()



async def delete_messages(message: types.Message):
    for i in range(message.message_id, 1, -1):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=i)
        except:
            pass


def register_handlers_auth(dp: Dispatcher):
    dp.register_message_handler(tg_auth, commands="start", state="*")
    dp.register_message_handler(tg_auth, Text(equals="Авторизация", ignore_case=True), state="*")
    dp.register_message_handler(tg_logout, commands="logout", state="*")
    dp.register_message_handler(tg_logout, Text(equals="Сменить пользователя", ignore_case=True), state="*")
    dp.register_message_handler(tg_insert_login, state=Booking.waiting_for_login)
    dp.register_message_handler(tg_insert_pass, state=Booking.waiting_for_password)
