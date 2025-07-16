import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CREATIO_BASE_URL")
IDENTITY_SERVICE_URL = os.getenv("CREATIO_IDENTITY_SERVICE_URL")
CLIENT_ID = os.getenv("CREATIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("CREATIO_CLIENT_SECRET")

# Кешуємо токен, щоб не робити зайвих запитів
CREATIO_TOKEN = None

async def get_access_token():
    global CREATIO_TOKEN
    if CREATIO_TOKEN:
        return CREATIO_TOKEN
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{IDENTITY_SERVICE_URL}/connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )
        resp.raise_for_status()
        CREATIO_TOKEN = resp.json()["access_token"]
        return CREATIO_TOKEN

async def create_or_get_chat(account_id, group_id):
    token = await get_access_token()
    data = {
        "AccountId": account_id,
        "Source": "Telegram",
        "AdditionalInfo": f"Group: {group_id}"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/rest/ChatApiService/CreateChat",
            json=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        r.raise_for_status()
        return r.json().get("ChatId")

async def post_message(chat_id, author_name, text):
    token = await get_access_token()
    data = {
        "ChatId": chat_id,
        "AuthorName": author_name,
        "MessageText": text
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/rest/ChatApiService/PostMessage",
            json=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        r.raise_for_status()
        return r.json()
