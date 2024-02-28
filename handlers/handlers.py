"""хендлеры"""

import json
from os import path, makedirs
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config_data.config import bot
import SupportedMediaFilter

router: Router = Router()
makedirs("files", exist_ok=True)
if not path.exists("files/users_ids.json"):
    with open("files/users_ids.json", "w", encoding="utf-8") as f:
        json.dump([], f)
if not path.exists("files/admins_ids.json"):
    with open("files/admins_ids.json", "w", encoding="utf-8") as f:
        json.dump([], f)

with open("files/users_ids.json", "r", encoding="utf-8") as f:
    users_ids = json.load(f)
with open("files/admins_ids.json", "r", encoding="utf-8") as f:
    admins_ids = json.load(f)


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    """запуск бота, создание необходимых файлов"""
    global users_ids
    global admins_ids
    if message.chat.id not in users_ids:
        users_ids.append(message.chat.id)
        for admin in admins_ids:
            await bot.send_message(
                chat_id=admin,
                text=f"Появился новый пользователь #id{str(message.chat.id)} {message.from_user.username}",
            )
        with open("files/users_ids.json", "w", encoding="utf-8") as f:
            json.dump(users_ids, f)


def extract_id(message: Message) -> int:
    """
    Извлекает ID юзера из хэштега в сообщении

    :param message: сообщение, из хэштега в котором нужно достать айди пользователя
    :return: ID пользователя, извлечённый из хэштега в сообщении
    """
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.entities or message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-1].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].extract_from(message.text or message.caption)
    if (
        len(hashtag) < 4 or not hashtag[3:].isdigit()
    ):  # либо просто #id, либо #idНЕЦИФРЫ
        raise ValueError("Некорректный ID для ответа!")

    return int(hashtag[3:])


@router.message(F.reply_to_message)
async def reply_to_user(message: Message):
    """ """
    user_id = extract_id(message.reply_to_message)
    await message.copy_to(user_id)


@router.message(F.text)
async def send_message(message: Message):
    """отправка сообщения админу"""
    global admins_ids
    chat_id = message.chat.id
    mes = message.html_text
    if chat_id in admins_ids and message.text[:4:] == "@all":
        with open("files/users_ids.json", encoding="utf-8") as f:
            user_list = json.load(f)
        for user in user_list:
            await bot.send_message(chat_id=user, text=mes[4:])
    elif message.chat.id not in admins_ids:
        user_chat_id: int = message.chat.id
        for admin in admins_ids:
            await bot.send_message(
                chat_id=admin,
                text=f"#id{str(user_chat_id)} {message.from_user.username}\n{message.html_text}",
            )


@router.message(SupportedMediaFilter.SupportedMediaFilter())
async def supported_media(message: Message):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)
    """
    global admins_ids
    for admin in admins_ids:
        await message.copy_to(
            chat_id=admin,
            caption=(
                (message.caption or "")
                + f"\n\n#id{message.from_user.id} {message.from_user.username}"
            ),
            parse_mode="HTML",
        )


@router.message()
async def unsupported_types(message: Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись
    """
    global admins_ids
    for admin in admins_ids:
        await message.copy_to(chat_id=admin)
        await bot.send_message(
            chat_id=admin,
            text=f"#id{str(message.chat.id)} {message.from_user.username}",
        )
