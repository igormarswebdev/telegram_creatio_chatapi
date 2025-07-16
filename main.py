import logging
from fastapi import FastAPI
from bot import bot, setup_bot
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
dp: Dispatcher = setup_bot()

@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Стартуємо Telegram бота через polling...")
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))

@app.post("/creatio-to-telegram")
async def send_message(data: dict):
    """
    Очікуваний payload:
    {
      "group_id": -123456789,
      "operator_name": "Олена",
      "text": "Доброго дня!"
    }
    """
    logger.info(f"➡ Отримано з Creatio: {data}")
    t_bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    msg_text = f"👨‍💼 *{data['operator_name']}*: {data['text']}"
    await t_bot.send_message(
        chat_id=data["group_id"],
        text=msg_text,
        parse_mode="Markdown"
    )
    await t_bot.session.close()
    logger.info(f"✅ Повідомлення надіслано в Telegram групу {data['group_id']}")
    return {"status": "sent"}
