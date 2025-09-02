#!/usr/bin/env python3
"""
Update timezone for existing users based on their language
"""
import asyncio
import logging
from database import DatabaseManager, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_user_timezone(user_id: int):
    """Update timezone for a specific user"""
    print(f"=== Updating timezone for user {user_id} ===")
    
    # Initialize database
    await init_db()
    
    # Get user
    user = await DatabaseManager.get_user(user_id)
    if not user:
        print(f"❌ User {user_id} not found!")
        return
    
    print(f"Current user data:")
    print(f"  Language: {user.language}")
    print(f"  Timezone: {user.timezone}")
    print(f"  Notification time: {user.notification_time}")
    
    # Determine correct timezone based on language
    timezone_map = {
        "ru": "Europe/Kiev",  # Russian speakers likely in Ukraine/Russia
        "uk": "Europe/Kiev",  # Ukrainian speakers in Ukraine
        "en": "UTC"           # English speakers - keep UTC
    }
    
    new_timezone = timezone_map.get(user.language, "UTC")
    
    if user.timezone != new_timezone:
        print(f"Updating timezone from '{user.timezone}' to '{new_timezone}'")
        
        # Update user timezone
        await DatabaseManager.create_or_update_user(user_id, timezone=new_timezone)
        
        # Log the change
        await DatabaseManager.log_action(
            user_id, 
            "timezone_updated", 
            {"old_timezone": user.timezone, "new_timezone": new_timezone}
        )
        
        print("✅ Timezone updated successfully!")
    else:
        print("✅ Timezone is already correct!")


async def main():
    """Main function"""
    # Your user ID
    user_id = 1903002179
    
    await update_user_timezone(user_id)
    
    print("\n=== Update completed ===")
    print("Теперь ваши уведомления будут приходить в правильное время!")
    print("Если вы установили время 19:45, уведомление придет в 19:45 по киевскому времени.")


if __name__ == "__main__":
    asyncio.run(main())
