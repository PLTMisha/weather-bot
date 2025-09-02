#!/usr/bin/env python3
"""
Temporary polling bot while Render token is being updated
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import settings
from database import init_db
from bot import weather_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_polling_bot():
    """Run bot with polling temporarily"""
    print("=== Временный запуск бота через Polling ===")
    print("Этот бот будет работать пока вы не обновите токен на Render")
    print("Отправьте /start боту @weathertownsbot")
    print("Для остановки нажмите Ctrl+C")
    print()
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Create bot and dispatcher
        bot = Bot(token=settings.telegram_bot_token)
        dp = Dispatcher()
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        
        # Delete webhook to avoid conflicts
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted for polling")
        
        # Register all handlers from weather_bot
        weather_bot.register_handlers()
        
        # Copy handlers to our dispatcher
        dp.message.handlers = weather_bot.dp.message.handlers
        dp.callback_query.handlers = weather_bot.dp.callback_query.handlers
        
        print("✅ Handlers registered")
        print("🚀 Starting polling...")
        print("Бот готов к работе!")
        
        # Start polling
        await dp.start_polling(bot, skip_updates=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Остановка бота...")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    finally:
        try:
            await bot.session.close()
        except:
            pass
        print("✅ Bot stopped")

if __name__ == "__main__":
    asyncio.run(run_polling_bot())
