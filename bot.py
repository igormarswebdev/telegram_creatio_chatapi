from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from telegram_groups import TELEGRAM_GROUPS_TO_ACCOUNT
from creatio_api import create_or_get_chat, post_message
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def handle_group_message(message: Message):
    if message.chat.id in TELEGRAM_GROUPS_TO_ACCOUNT:
        account_id = TELEGRAM_GROUPS_TO_ACCOUNT[message.chat.id]
        author_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        text = message.text

        chat_id = await create_or_get_chat(account_id, message.chat.id)
        await post_message(chat_id, author_name, text)

        await message.reply("✅ Повідомлення передано в Creatio")

def setup_bot():
    return dp
