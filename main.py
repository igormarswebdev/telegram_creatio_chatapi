from fastapi import FastAPI
from bot import bot, setup_bot
from aiogram import Dispatcher
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

app = FastAPI()
dp: Dispatcher = setup_bot()

@app.on_event("startup")
async def on_startup():
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))

@app.post("/creatio-to-telegram")
async def send_message(data: dict):
    """
    data = {
      "group_id": -123456789,
      "operator_name": "Олена",
      "text": "Доброго дня!"
    }
    """
    from aiogram import Bot
    t_bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    await t_bot.send_message(
        chat_id=data["group_id"],
        text=f"👨‍💼 *{data['operator_name']}*: {data['text']}",
        parse_mode="Markdown"
    )
    return {"status": "sent"}
