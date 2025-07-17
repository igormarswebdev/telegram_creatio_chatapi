from aiogram import Bot, Dispatcher
from aiogram.types import Message
from creatio_api import create_or_get_chat, post_message, find_account_by_telegram_chat
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

    try:
        account_id = await find_account_by_telegram_chat(message.chat.id)

        if account_id:
            author_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
            text = message.text

            print(f"🔗 Прив’язано до Account ID: {account_id}")
            print(f"👤 Автор повідомлення: {author_name}")

            chat_id = await create_or_get_chat(account_id, message.chat.id)
            print(f"💬 ChatId у Creatio: {chat_id}")

            await post_message(chat_id, author_name, text)
            print("✅ Повідомлення передано у Creatio")
            await message.reply("✅ Повідомлення передано в Creatio")

        else:
            print("⚠️ Не знайдено пов’язаний Account у Creatio. Створимо чат без прив’язки.")
            author_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
            text = message.text

            chat_id = await create_or_get_chat(None, message.chat.id)
            print(f"💬 ChatId (без прив’язки): {chat_id}")
            await post_message(chat_id, author_name, text)
            await message.reply("✅ Повідомлення збережено. Можна буде пізніше прив’язати до контрагента.")

    except Exception as e:
        print(f"❌ Помилка при обробці повідомлення: {e}")
        await message.reply("⚠️ Сталася помилка при обробці повідомлення.")
