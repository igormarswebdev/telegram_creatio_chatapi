import os
import logging
from fastapi import FastAPI, Request
from bot import bot, dp
from aiogram.types import Update
from dotenv import load_dotenv
from voice_manager import handle_incoming_call, handle_voice_input, handle_voice_status_callback

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Telegram Creatio ChatAPI с голосовым менеджером")

WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}/webhook"

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook встановлено на {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logging.info("Webhook видалено")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def health_check():
    return {
        "status": "ok", 
        "services": ["telegram_bot", "voice_manager"],
        "description": "Telegram Bot с интеграцией Creatio и голосовым менеджером для интернет магазина"
    }

# Голосовые endpoints
@app.post("/voice/incoming")
async def voice_incoming_call(request: Request):
    """Обработка входящих звонков через Twilio"""
    return await handle_incoming_call(request)

@app.post("/voice/handle-input")
async def voice_handle_input(request: Request):
    """Обработка пользовательского ввода во время звонка"""
    return await handle_voice_input(request)

@app.post("/voice/status")
async def voice_status_callback(request: Request):
    """Обработка статусных сообщений о звонках"""
    return await handle_voice_status_callback(request)
