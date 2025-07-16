from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TelegramMessage(BaseModel):
    chat_id: int
    text: str

@app.post("/from-telegram")
async def from_telegram(msg: TelegramMessage):
    print(f"🔔 NEW MESSAGE FROM TELEGRAM:")
    print(f"Chat ID: {msg.chat_id}")
    print(f"Text: {msg.text}")
    return {"status": "logged"}
