#!/usr/bin/env python3
"""
Test script for timezone-aware notifications
"""
import asyncio
import logging
from datetime import datetime, time
import pytz

from database import DatabaseManager, init_db
from scheduler import notification_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_timezone_notifications():
    """Test timezone-aware notification system"""
    print("=== Testing Timezone-Aware Notifications ===")
    
    # Initialize database
    await init_db()
    
    # Test user ID (your ID)
    test_user_id = 1903002179
    
    # Get current time in different timezones
    utc_now = datetime.now(pytz.UTC)
    kiev_tz = pytz.timezone('Europe/Kiev')
    kiev_now = utc_now.astimezone(kiev_tz)
    
    print(f"Current UTC time: {utc_now.strftime('%H:%M:%S')}")
    print(f"Current Kiev time: {kiev_now.strftime('%H:%M:%S')}")
    
    # Check if user exists
    user = await DatabaseManager.get_user(test_user_id)
    if user:
        print(f"User found:")
        print(f"  Language: {user.language}")
        print(f"  Timezone: {user.timezone}")
        print(f"  Notification time: {user.notification_time}")
        print(f"  Notifications enabled: {user.notifications_enabled}")
        
        # Test notification matching logic
        if user.notification_time:
            user_tz = pytz.timezone(user.timezone if user.timezone != "UTC" else "Europe/Kiev")
            user_local_time = utc_now.astimezone(user_tz)
            
            print(f"\nNotification matching test:")
            print(f"  User's local time: {user_local_time.strftime('%H:%M:%S')}")
            print(f"  User's notification time: {user.notification_time}")
            
            if (user_local_time.hour == user.notification_time.hour and 
                user_local_time.minute == user.notification_time.minute):
                print("  ✅ Time matches - notification would be sent!")
            else:
                print("  ❌ Time doesn't match - no notification")
                
                # Calculate when next notification would be sent
                next_notification_utc = user_local_time.replace(
                    hour=user.notification_time.hour,
                    minute=user.notification_time.minute,
                    second=0,
                    microsecond=0
                )
                if next_notification_utc <= user_local_time:
                    next_notification_utc = next_notification_utc.replace(day=next_notification_utc.day + 1)
                
                next_notification_utc = next_notification_utc.astimezone(pytz.UTC)
                print(f"  Next notification at: {next_notification_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"  That's in Kiev time: {next_notification_utc.astimezone(kiev_tz).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("User not found!")
    
    # Test the actual notification system
    print(f"\n=== Testing notification system for current UTC time ===")
    current_utc_time = utc_now.strftime("%H:%M")
    print(f"Checking for users with notifications at UTC {current_utc_time}")
    
    users_for_notification = await DatabaseManager.get_users_for_notification(current_utc_time)
    print(f"Found {len(users_for_notification)} users for notification")
    
    for user in users_for_notification:
        print(f"  User {user.user_id}: {user.language}, timezone: {user.timezone}, time: {user.notification_time}")


async def send_test_notification_now():
    """Send a test notification immediately"""
    print("\n=== Sending Test Notification ===")
    
    test_user_id = 1903002179
    
    try:
        await notification_scheduler.send_test_notification(test_user_id)
        print("✅ Test notification sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test notification: {e}")


async def main():
    """Main test function"""
    await test_timezone_notifications()
    
    # Ask if user wants to send test notification
    print("\n" + "="*50)
    response = input("Send test notification now? (y/n): ").lower().strip()
    if response == 'y':
        await send_test_notification_now()
    
    print("\n=== Test completed ===")


if __name__ == "__main__":
    asyncio.run(main())
