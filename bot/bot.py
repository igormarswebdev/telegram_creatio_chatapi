import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
API_URL = os.getenv("API_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    user = message.from_user
    formatted_text = f"[{user.full_name} (@{user.username})]: {message.text}"
    async with aiohttp.ClientSession() as session:
        await session.post(f"{API_URL}/from-telegram", json={
            "chat_id": message.chat.id,
            "text": formatted_text
        })
    await message.answer("✅ Передано у Creatio.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
