from fastapi import FastAPI
from pydantic import BaseModel
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

CREATIO_URL = os.getenv("CREATIO_URL")
CLIENT_ID = os.getenv("CREATIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("CREATIO_CLIENT_SECRET")
USERNAME = os.getenv("CREATIO_USERNAME")
PASSWORD = os.getenv("CREATIO_PASSWORD")
CHAT_TYPE_ID = os.getenv("CREATIO_CHAT_TYPE_ID")
OWNER_ID = os.getenv("CREATIO_OWNER_ID")

app = FastAPI()
chat_store = {}

class TelegramMessage(BaseModel):
    chat_id: int
    text: str
      
async def get_creatio_token():
    print("URL:", f"{CREATIO_URL}connect/token")
    print("DATA:", {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    })
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CREATIO_URL}connect/token",
            data={
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "username": USERNAME,
                "password": PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as resp:
            text = await resp.text()
            print("DEBUG RESPONSE TEXT:", text)
            try:
                data = await resp.json()
                return data.get("access_token")
            except Exception as e:
                print("ERROR parsing JSON:", e)
                return None

async def create_chat(token, telegram_chat_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CREATIO_URL}odata/Chat",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "Name": f"Support chat for Telegram {telegram_chat_id}",
                "TypeId": CHAT_TYPE_ID,
                "OwnerId": OWNER_ID
            }
        ) as resp:
            data = await resp.json()
            return data.get("Id")

async def add_message(token, creatio_chat_id, text, author_id=None):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{CREATIO_URL}odata/ChatMessage",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "ChatId": creatio_chat_id,
                "Message": text,
                "AuthorId": author_id
            }
        )

@app.post("/from-telegram")
async def from_telegram(msg: TelegramMessage):
    token = await get_creatio_token()
    if msg.chat_id not in chat_store:
        creatio_chat_id = await create_chat(token, msg.chat_id)
        chat_store[msg.chat_id] = creatio_chat_id
    else:
        creatio_chat_id = chat_store[msg.chat_id]
    await add_message(token, creatio_chat_id, msg.text)
    return {"status": "done", "creatio_chat_id": creatio_chat_id}
