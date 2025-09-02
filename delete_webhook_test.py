#!/usr/bin/env python3
"""
Delete webhook and test polling
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import settings
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def delete_webhook_and_test():
    """Delete webhook and test with polling"""
    print("=== Deleting Webhook and Testing Polling ===")
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Delete webhook
        print("Удаляем webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        
        # Check webhook status
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook URL after deletion: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        
        if not webhook_info.url:
            print("✅ Webhook successfully removed")
            
            # Initialize database
            await init_db()
            print("✅ Database initialized")
            
            # Create dispatcher
            dp = Dispatcher()
            
            # Simple start handler
            @dp.message(Command("start"))
            async def cmd_start_test(message: Message):
                logger.info(f"Received /start from user {message.from_user.id}")
                await message.answer("🎉 Бот работает через polling! Обработчики команд функционируют правильно.")
                print(f"✅ Processed /start from {message.from_user.first_name}")
            
            print("✅ Handlers registered")
            print("🚀 Starting polling for 30 seconds...")
            print("Отправьте /start боту @mishatgtestbot прямо сейчас!")
            
            # Start polling with timeout
            try:
                await asyncio.wait_for(
                    dp.start_polling(bot, skip_updates=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                print("⏰ Polling timeout (30 seconds)")
            
            print("✅ Polling test completed")
        else:
            print("❌ Failed to delete webhook")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        try:
            await bot.session.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(delete_webhook_and_test())
