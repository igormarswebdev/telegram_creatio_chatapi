import os
import logging
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from creatio_api import create_or_get_chat, post_message
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class VoiceManager:
    """Голосовий менеджер для інтернет магазину"""
    
    def __init__(self):
        self.store_name = "Інтернет Магазин"
        self.phone_number = os.getenv("STORE_PHONE_NUMBER", "+380991234567")
        self.working_hours = "Пн-Пт 9:00-18:00, Сб-Нд 10:00-16:00"
        
    def generate_welcome_message(self) -> str:
        """Привітальне повідомлення"""
        return (
            f"Вітаємо у {self.store_name}! "
            "Для отримання інформації про товари натисніть 1, "
            "для перевірки статусу замовлення натисніть 2, "
            "для зв'язку з оператором натисніть 3, "
            "для отримання контактної інформації натисніть 4."
        )
    
    def handle_product_inquiry(self) -> str:
        """Обробка запитів про товари"""
        return (
            "Наш каталог включає електроніку, одяг, товари для дому та спорту. "
            "Для детальної консультації натисніть 0 для зв'язку з консультантом, "
            "або відвідайте наш сайт."
        )
    
    def handle_order_status(self) -> str:
        """Обробка запитів про статус замовлення"""
        return (
            "Для перевірки статусу замовлення введіть номер замовлення після звукового сигналу. "
            "Або натисніть 0 для зв'язку з оператором."
        )
    
    def handle_contact_info(self) -> str:
        """Контактна інформація"""
        return (
            f"Наші контакти: телефон {self.phone_number}, "
            f"режим роботи: {self.working_hours}. "
            "Ми також доступні в Telegram боті для швидкого зв'язку."
        )
    
    def handle_transfer_to_operator(self) -> str:
        """Переведення на оператора"""
        return (
            "Перевожу вас на оператора. Будь ласка, залишайтесь на лінії. "
            "Час очікування може становити до 3 хвилин."
        )
    
    def generate_twiml_response(self, message: str, gather_options: bool = True) -> str:
        """Генерація TwiML відповіді для Twilio"""
        if gather_options:
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather timeout="10" numDigits="1" action="/voice/handle-input" method="POST">
        <Say language="uk" voice="Polly.Ruslana">{message}</Say>
    </Gather>
    <Say language="uk" voice="Polly.Ruslana">Дякуємо за дзвінок. До побачення!</Say>
    <Hangup/>
</Response>'''
        else:
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="uk" voice="Polly.Ruslana">{message}</Say>
    <Hangup/>
</Response>'''

voice_manager = VoiceManager()

async def handle_incoming_call(request: Request) -> Response:
    """Обробка вхідного дзвінка"""
    form_data = await request.form()
    caller_phone = form_data.get("From", "Unknown")
    call_sid = form_data.get("CallSid", "Unknown")
    
    logger.info(f"📞 Вхідний дзвінок від {caller_phone}, CallSid: {call_sid}")
    
    try:
        # Створюємо чат у Creatio для логування дзвінка
        chat_id = await create_or_get_chat(None, f"phone:{caller_phone}")
        await post_message(
            chat_id, 
            "Voice Manager", 
            f"Вхідний дзвінок від {caller_phone}"
        )
        logger.info(f"✅ Дзвінок залогований у Creatio, ChatId: {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Помилка при логуванні дзвінка: {e}")
    
    welcome_message = voice_manager.generate_welcome_message()
    twiml_response = voice_manager.generate_twiml_response(welcome_message)
    
    return PlainTextResponse(twiml_response, media_type="application/xml")

async def handle_voice_input(request: Request) -> Response:
    """Обробка введення користувача через телефон"""
    form_data = await request.form()
    digits = form_data.get("Digits", "")
    caller_phone = form_data.get("From", "Unknown")
    call_sid = form_data.get("CallSid", "Unknown")
    
    logger.info(f"🔢 Отримано цифру {digits} від {caller_phone}")
    
    try:
        # Логування дії користувача
        chat_id = await create_or_get_chat(None, f"phone:{caller_phone}")
        await post_message(
            chat_id, 
            caller_phone, 
            f"Обрано опцію: {digits}"
        )
        
        # Обробка введення користувача
        if digits == "1":
            response_message = voice_manager.handle_product_inquiry()
            await post_message(chat_id, "Voice Manager", "Інформація про товари")
        elif digits == "2":
            response_message = voice_manager.handle_order_status()
            await post_message(chat_id, "Voice Manager", "Перевірка статусу замовлення")
        elif digits == "3":
            response_message = voice_manager.handle_transfer_to_operator()
            await post_message(chat_id, "Voice Manager", "Переведення на оператора")
        elif digits == "4":
            response_message = voice_manager.handle_contact_info()
            await post_message(chat_id, "Voice Manager", "Контактна інформація")
        else:
            response_message = "Невірний вибір. " + voice_manager.generate_welcome_message()
            await post_message(chat_id, "Voice Manager", f"Невірний вибір: {digits}")
        
        logger.info(f"📝 Дія залогована у Creatio")
        
    except Exception as e:
        logger.error(f"❌ Помилка при обробці введення: {e}")
        response_message = "Виникла технічна помилка. Спробуйте пізніше або зв'яжіться з нами за телефоном."
    
    # Для опцій 1, 2, 4 даємо можливість повернутися до меню
    gather_options = digits in ["1", "2", "4"]
    if gather_options:
        response_message += " Натисніть 0 для повернення до головного меню."
    
    twiml_response = voice_manager.generate_twiml_response(
        response_message, 
        gather_options
    )
    
    return PlainTextResponse(twiml_response, media_type="application/xml")

async def handle_voice_status_callback(request: Request) -> Response:
    """Обробка статусних повідомлень про дзвінки"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "Unknown")
    call_status = form_data.get("CallStatus", "Unknown")
    caller_phone = form_data.get("From", "Unknown")
    duration = form_data.get("CallDuration", "0")
    
    logger.info(f"📈 Статус дзвінка {call_sid}: {call_status}, тривалість: {duration}с")
    
    try:
        # Логування завершення дзвінка
        chat_id = await create_or_get_chat(None, f"phone:{caller_phone}")
        await post_message(
            chat_id, 
            "Voice Manager", 
            f"Дзвінок завершено. Статус: {call_status}, тривалість: {duration}с"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка при логуванні статусу дзвінка: {e}")
    
    return {"status": "ok"}