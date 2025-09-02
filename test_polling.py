#!/usr/bin/env python3
"""
Test bot with polling instead of webhook to check if handlers work
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import settings
from database import init_db, DatabaseManager
from bot import weather_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_polling():
    """Test bot with polling"""
    print("=== Testing Bot with Polling ===")
    print("Этот тест запустит бота в режиме polling на 30 секунд")
    print("Отправьте /start боту @mishatgtestbot в Telegram")
    print("Если бот ответит, значит проблема в webhook")
    print("Если не ответит, значит проблема в обработчиках")
    print()
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Create bot and dispatcher
        bot = Bot(token=settings.telegram_bot_token)
        dp = Dispatcher()
        
        # Simple start handler for testing
        @dp.message(Command("start"))
        async def cmd_start_test(message: Message):
            logger.info(f"Received /start from user {message.from_user.id}")
            await message.answer("🎉 Бот работает! Обработчики команд функционируют правильно.")
            print(f"✅ Processed /start from {message.from_user.first_name}")
        
        # Register all original handlers
        weather_bot.register_handlers()
        
        print("✅ Handlers registered")
        print("🚀 Starting polling for 30 seconds...")
        print("Отправьте /start боту прямо сейчас!")
        
        # Start polling with timeout
        try:
            await asyncio.wait_for(
                dp.start_polling(bot, skip_updates=True),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            print("⏰ Polling timeout (30 seconds)")
        
        print("✅ Polling test completed")
        
    except Exception as e:
        logger.error(f"Error in polling test: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        try:
            await bot.session.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_polling())
