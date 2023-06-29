import asyncio
import logging
from aiogram import Bot, types
from aiogram.types import BotCommand

from botApp.create_bot import bot, dp
from botApp.handlers import tg_auth

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Авторизация"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    tg_auth.register_handlers_auth(dp)
    # wheel.register_handlers_client(dp)
    # booking.register_handlers_client(dp)

    await set_commands(bot)

    await dp.start_polling()


# @dp.message_handler(content_types=types.ContentTypes.ANY)
# async def handle_all_messages(message: types.Message):
#     # Ваш код обработки сообщения здесь
#     print(message)
#     # if await dp.current_state().get_state() is None:
#         # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


if __name__ == '__main__':
    asyncio.run(main())
