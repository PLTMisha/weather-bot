#!/usr/bin/env python3
"""
Скрипт для исправления проблем с webhook на Render.com
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from bot import weather_bot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_webhook():
    """Настройка webhook для бота"""
    try:
        # URL webhook для Render.com
        webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
        
        logger.info("Удаляем существующий webhook...")
        await weather_bot.bot.delete_webhook(drop_pending_updates=True)
        
        logger.info(f"Устанавливаем новый webhook: {webhook_url}")
        result = await weather_bot.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        if result:
            logger.info("✅ Webhook успешно установлен!")
            
            # Проверяем информацию о webhook
            webhook_info = await weather_bot.bot.get_webhook_info()
            logger.info(f"URL webhook: {webhook_info.url}")
            logger.info(f"Ожидающих обновлений: {webhook_info.pending_update_count}")
            
            if webhook_info.last_error_date:
                logger.warning(f"Последняя ошибка: {webhook_info.last_error_message}")
            else:
                logger.info("✅ Ошибок нет!")
                
        else:
            logger.error("❌ Не удалось установить webhook")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при настройке webhook: {e}")
    finally:
        await weather_bot.bot.session.close()


async def test_bot_connection():
    """Тестирование подключения к боту"""
    try:
        logger.info("Тестируем подключение к боту...")
        me = await weather_bot.bot.get_me()
        logger.info(f"✅ Бот подключен: @{me.username} ({me.first_name})")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к боту: {e}")
        return False


async def main():
    """Основная функция"""
    logger.info("🔧 Исправление проблем с webhook...")
    
    # Проверяем переменные окружения
    if not settings.telegram_bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    logger.info(f"🔑 Токен бота: {settings.telegram_bot_token[:10]}...")
    
    # Тестируем подключение
    if not await test_bot_connection():
        return
    
    # Настраиваем webhook
    await setup_webhook()
    
    logger.info("✅ Исправление завершено!")


if __name__ == "__main__":
    asyncio.run(main())
