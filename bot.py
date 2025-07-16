import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from telegram_groups import TELEGRAM_GROUPS_TO_ACCOUNT
from creatio_api import create_or_get_chat, post_message

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def handle_group_message(message: Message):
    logger.info(f"👉 Отримано повідомлення в групі {message.chat.id}: {message.text}")
    
    if message.chat.id in TELEGRAM_GROUPS_TO_ACCOUNT:
        account_id = TELEGRAM_GROUPS_TO_ACCOUNT[message.chat.id]
        author_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        text = message.text

        logger.info(f"📌 Знайдено відповідність group_id={message.chat.id} -> account_id={account_id}")
        logger.info(f"✍ Автор: {author_name}")

        chat_id = await create_or_get_chat(account_id, message.chat.id)
        logger.info(f"💬 Отриманий або створений ChatId в Creatio: {chat_id}")

        await post_message(chat_id, author_name, text)
        logger.info(f"✅ Повідомлення '{text}' відправлено в Creatio")

        await message.reply("✅ Повідомлення передано в Creatio")
    else:
        logger.warning(f"⚠ Група {message.chat.id} не знайдена у TELEGRAM_GROUPS_TO_ACCOUNT. Повідомлення пропущено.")

def setup_bot():
    return dp
