import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List
import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import settings, KEEP_ALIVE_INTERVAL
from database import DatabaseManager, User
from weather_api import weather_api
from bot import weather_bot
from localization import _
from city_timezone_mapper import format_local_time

logger = logging.getLogger(__name__)


class NotificationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot = weather_bot.bot
        self.processing_notifications = False
        
    async def start(self):
        try:
            self.scheduler.add_job(
                self.keep_alive_ping,
                IntervalTrigger(seconds=KEEP_ALIVE_INTERVAL),
                id="keep_alive",
                name="Keep Alive Ping"
            )
            
            # Optimized: Check every minute instead of creating 1440 jobs
            self.scheduler.add_job(
                self.check_notifications,
                CronTrigger(second=0),  # Run every minute at second 0
                id="notification_checker",
                name="Notification Checker"
            )
            
            self.scheduler.start()
            logger.info("Optimized scheduler started with single checker job")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def keep_alive_ping(self):
        try:
            import httpx
            
            if settings.webhook_url:
                base_url = settings.webhook_url.replace("/webhook", "")
                health_url = f"{base_url}/health"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(health_url, timeout=10)
                    if response.status_code == 200:
                        logger.debug("Keep-alive ping successful")
                    else:
                        logger.warning(f"Keep-alive ping returned status {response.status_code}")
            
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
    
    async def check_notifications(self):
        if self.processing_notifications:
            logger.debug("Skipping notification check - already processing")
            return
            
        try:
            self.processing_notifications = True
            current_time = datetime.now()
            time_str = f"{current_time.hour:02d}:{current_time.minute:02d}"
            
            users = await DatabaseManager.get_users_for_notification(time_str)
            
            if users:
                logger.info(f"Processing {len(users)} notifications for {time_str}")
                
                # Process in batches to avoid overwhelming the system
                batch_size = 10  # Increased batch size
                for i in range(0, len(users), batch_size):
                    batch = users[i:i + batch_size]
                    
                    # Process batch concurrently but with limited concurrency
                    tasks = [self.send_weather_notification(user) for user in batch]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Reduced delay between batches
                    if i + batch_size < len(users):
                        await asyncio.sleep(0.1)  # Reduced from 0.5 to 0.1
                        
        except Exception as e:
            logger.error(f"Error in check_notifications: {e}")
        finally:
            self.processing_notifications = False
    
    async def send_scheduled_notifications(self, notification_time: str):
        """Send notifications to users at specified time"""
        try:
            # Get users who should receive notifications at this time
            users = await DatabaseManager.get_users_for_notification(notification_time)
            
            if not users:
                return
            
            logger.info(f"Sending notifications to {len(users)} users at {notification_time}")
            
            # Send notifications to each user
            for user in users:
                try:
                    await self.send_weather_notification(user)
                    await asyncio.sleep(0.05)  # Reduced delay to avoid rate limiting
                    
                except Exception as e:
                    logger.error(f"Failed to send notification to user {user.user_id}: {e}")
                    await DatabaseManager.log_action(
                        user.user_id, 
                        "notification_failed", 
                        {"error": str(e), "time": notification_time}
                    )
            
        except Exception as e:
            logger.error(f"Error in send_scheduled_notifications: {e}")
    
    async def send_weather_notification(self, user: User):
        """Send weather notification to a specific user"""
        try:
            if not user.city or not user.city_lat or not user.city_lon:
                logger.warning(f"User {user.user_id} has incomplete location data")
                return
            
            # Get weather data
            weather_data = await weather_api.get_weather_forecast(
                float(user.city_lat),
                float(user.city_lon),
                user.language
            )
            
            if not weather_data:
                logger.error(f"Failed to get weather data for user {user.user_id}")
                return
            
            # Format message
            message = await self.format_notification_message(
                weather_data, 
                user.city, 
                user.language,
                float(user.city_lat),
                float(user.city_lon)
            )
            
            # Create keyboard
            keyboard = await weather_bot.get_weather_keyboard(user.language)
            
            # Send message
            await self.bot.send_message(
                chat_id=user.user_id,
                text=message,
                reply_markup=keyboard
            )
            
            # Log successful notification
            await DatabaseManager.log_action(
                user.user_id,
                "notification_sent",
                {
                    "city": user.city,
                    "temperature": weather_data.get("current_temperature"),
                    "time": str(user.notification_time)[:5]
                }
            )
            
            logger.debug(f"Notification sent to user {user.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification to user {user.user_id}: {e}")
            raise
    
    async def format_notification_message(self, weather_data: dict, city: str, language: str, city_lat: float, city_lon: float) -> str:
        """Format weather notification message"""
        # Get local date for the city
        local_date, local_time = format_local_time(city_lat, city_lon)
        # Convert date format from DD.MM.YYYY to YYYY-MM-DD
        day, month, year = local_date.split('.')
        today = f"{year}-{month}-{day}"
        
        # Get clothing recommendation
        clothing_advice = weather_api.get_clothing_recommendation(weather_data, language)
        
        message = _("weather_in", language, city=city, date=today) + "\n\n"
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
    
    async def send_test_notification(self, user_id: int):
        """Send a test notification to a user (for testing purposes)"""
        try:
            user = await DatabaseManager.get_user(user_id)
            if user:
                await self.send_weather_notification(user)
                logger.info(f"Test notification sent to user {user_id}")
            else:
                logger.error(f"User {user_id} not found for test notification")
                
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
    
    def get_scheduler_status(self) -> dict:
        """Get scheduler status information"""
        try:
            jobs = self.scheduler.get_jobs()
            return {
                "running": self.scheduler.running,
                "job_count": len(jobs),
                "jobs": [
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    for job in jobs[:10]  # Limit to first 10 jobs for brevity
                ]
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {"error": str(e)}


# Global scheduler instance
notification_scheduler = NotificationScheduler()


# Utility functions for manual operations
async def send_manual_notification(user_id: int):
    """Send manual notification to a user"""
    await notification_scheduler.send_test_notification(user_id)


async def get_users_with_notifications_at_time(time_str: str) -> List[User]:
    """Get users who have notifications enabled at specific time"""
    return await DatabaseManager.get_users_for_notification(time_str)


async def schedule_status():
    """Get current scheduler status"""
    return notification_scheduler.get_scheduler_status()
