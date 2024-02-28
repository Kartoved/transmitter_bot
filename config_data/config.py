'''настройки бота'''

from dataclasses import dataclass
from environs import Env
from aiogram import Bot


@dataclass
class TgBot:
    '''создание класса бота'''
    token: str


@dataclass
class Config:
    '''создание класса бота'''
    tg_bot: TgBot


def load_config(path: str | None = None):
    '''загрузка токена из переменных окружения'''
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))


config = load_config()

bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')
