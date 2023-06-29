from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from botApp.botConfig import token, tg_admin_id, tg_chat_id

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
admin_id = tg_admin_id
chat_id = tg_chat_id
