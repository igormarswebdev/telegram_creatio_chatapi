import logging
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    logger.info(f"🔵 Створюємо або отримуємо чат в Creatio для AccountId={account_id}, GroupId={group_id}")
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/ChatService/CreateChat", json=data, headers=get_auth_headers())
        logger.info(f"➡ POST {BASE_URL}/ChatService/CreateChat payload={data}")
        logger.info(f"⬅ Response: {r.status_code} - {r.text}")
        r.raise_for_status()
        chat_id = r.json().get("ChatId")
        logger.info(f"✅ Отриманий ChatId: {chat_id}")
        return chat_id

async def post_message(chat_id, author_name, text):
    data = {
        "ChatId": chat_id,
        "AuthorName": author_name,
        "MessageText": text
    }
    logger.info(f"💬 Відправляємо повідомлення у Creatio: ChatId={chat_id}, Author={author_name}, Text='{text}'")
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/ChatService/PostMessage", json=data, headers=get_auth_headers())
        logger.info(f"➡ POST {BASE_URL}/ChatService/PostMessage payload={data}")
        logger.info(f"⬅ Response: {r.status_code} - {r.text}")
        r.raise_for_status()
        result = r.json()
        logger.info(f"✅ Результат від Creatio: {result}")
        return result
