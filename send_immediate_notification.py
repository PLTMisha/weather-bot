#!/usr/bin/env python3
"""
Скрипт для немедленной отправки тестового уведомления
"""
import asyncio
import logging
from datetime import datetime

from database import DatabaseManager, init_db
from weather_api import weather_api
from bot import weather_bot
from localization import _

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_immediate_notification(user_id: int):
    """Отправить уведомление пользователю прямо сейчас"""
    
    print(f"🚀 Отправка уведомления пользователю {user_id}...")
    
    try:
        # Инициализация
        await init_db()
        
        # Получить пользователя
        user = await DatabaseManager.get_user(user_id)
        if not user:
            print(f"❌ Пользователь {user_id} не найден")
            return
        
        print(f"✅ Пользователь найден: {user.city}, язык: {user.language}")
        
        if not user.city or not user.city_lat or not user.city_lon:
            print("❌ У пользователя не настроен город")
            return
        
        # Получить данные о погоде
        print("🌤 Получение данных о погоде...")
        weather_data = await weather_api.get_weather_forecast(
            float(user.city_lat),
            float(user.city_lon),
            user.language
        )
        
        if not weather_data:
            print("❌ Не удалось получить данные о погоде")
            return
        
        # Форматировать сообщение
        message = await format_notification_message(weather_data, user.city, user.language)
        
        # Создать клавиатуру
        keyboard = await weather_bot.get_weather_keyboard(user.language)
        
        # Отправить сообщение
        print("📤 Отправка сообщения...")
        await weather_bot.bot.send_message(
            chat_id=user.user_id,
            text=message,
            reply_markup=keyboard
        )
        
        # Записать в лог
        await DatabaseManager.log_action(
            user.user_id,
            "test_notification_sent",
            {
                "city": user.city,
                "temperature": weather_data.get("current_temperature"),
                "time": datetime.now().strftime("%H:%M")
            }
        )
        
        print("✅ Уведомление успешно отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")
        logger.error(f"Error sending notification: {e}", exc_info=True)
    
    finally:
        # Закрыть сессию бота
        await weather_bot.bot.session.close()


async def format_notification_message(weather_data: dict, city: str, language: str) -> str:
    """Форматировать сообщение уведомления"""
    now = datetime.now()
    today_date = now.strftime("%d.%m.%Y")
    current_time = now.strftime("%H:%M")
    
    # Получить рекомендацию по одежде
    clothing_advice = weather_api.get_clothing_recommendation(weather_data, language)
    
    # Включить дату и время в основной заголовок
    if language == "ru":
        weather_title = f"🌤 Погода в {city} на {today_date} в {current_time}"
    else:
        weather_title = f"🌤 Weather in {city} for {today_date} at {current_time}"
    
    message = weather_title + "\n\n"
    message += _("current_temp", language, 
                temp=weather_data["current_temperature"], 
                feels_like=weather_data["feels_like"]) + "\n"
    message += _("today_range", language, 
                min=weather_data["min_temperature"], 
                max=weather_data["max_temperature"]) + "\n"
    message += f"☁️ {weather_data['description']}\n"
    message += _("humidity", language, humidity=weather_data["humidity"]) + "\n"
    message += _("wind", language, speed=weather_data["wind_speed"]) + "\n"
    message += _("rain_prob", language, prob=weather_data["rain_probability"]) + "\n\n"
    message += _("recommendation", language, advice=clothing_advice) + "\n\n"
    message += _("have_great_day", language)
    
    return message


async def main():
    """Главная функция"""
    print("🔧 Тестовая отправка уведомления")
    print("=" * 40)
    
    # Найти пользователя с уведомлениями на 16:30
    await init_db()
    users = await DatabaseManager.get_users_for_notification("16:30")
    
    if users:
        user_id = users[0].user_id
        print(f"👤 Найден пользователь {user_id} с уведомлениями на 16:30")
        await send_immediate_notification(user_id)
    else:
        print("❌ Пользователей с уведомлениями на 16:30 не найдено")


if __name__ == "__main__":
    asyncio.run(main())
