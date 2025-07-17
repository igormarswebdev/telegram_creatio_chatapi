from aiogram import Bot, Dispatcher
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
    print(f"📥 Отримано повідомлення від @{message.from_user.username or message.from_user.id}")
    print(f"➡️   chat.id = {message.chat.id}")
    print(f"➡️   text = {message.text}")
    if message.chat.id in TELEGRAM_GROUPS_TO_ACCOUNT:
        account_id = TELEGRAM_GROUPS_TO_ACCOUNT[message.chat.id]
        author_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        text = message.text

        print(f"🔗 Прив’язано до Account ID: {account_id}")
        print(f"👤 Автор повідомлення: {author_name}")

        try:
            chat_id = await create_or_get_chat(account_id, message.chat.id)
            print(f"💬 ChatId у Creatio: {chat_id}")

            await post_message(chat_id, author_name, text)
            print("✅ Повідомлення передано у Creatio")

            await message.reply("✅ Повідомлення передано в Creatio")

        except Exception as e:
            print(f"❌ Помилка при відправці в Creatio: {e}")
            await message.reply("⚠️ Сталася помилка при передачі в Creatio.")
    else:
        #print("⚠️ Повідомлення з групи, яка не пов’язана з Creatio")
