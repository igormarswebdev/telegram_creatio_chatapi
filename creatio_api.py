import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CREATIO_BASE_URL")

def get_auth_headers():
    username = os.getenv("CREATIO_USERNAME")
    password = os.getenv("CREATIO_PASSWORD")
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

async def create_or_get_chat(account_id, group_id):
    data = {
        "AccountId": account_id,
        "Source": "Telegram",
        "AdditionalInfo": f"Group: {group_id}"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/ChatService/CreateChat", json=data, headers=get_auth_headers())
        r.raise_for_status()
        return r.json().get("ChatId")

async def post_message(chat_id, author_name, text):
    data = {
        "ChatId": chat_id,
        "AuthorName": author_name,
        "MessageText": text
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/ChatService/PostMessage", json=data, headers=get_auth_headers())
        r.raise_for_status()
        return r.json()
