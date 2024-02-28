"""исполняемый файл"""

import asyncio
from aiogram import Dispatcher
from config_data.config import bot
from keyboards.set_menu import set_main_menu
from handlers import handlers


async def main():
    dp: Dispatcher = Dispatcher()
    dp.include_router(handlers.router)
    await bot.delete_my_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
