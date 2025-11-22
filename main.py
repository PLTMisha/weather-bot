import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from database import init_db
from bot import weather_bot, dp
from scheduler import notification_scheduler
from monitoring import app_monitor, get_system_status
from weather_api import weather_api

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Weather Bot application...")
    
    try:
        await init_db()
        logger.info("Database initialized")
        
        weather_bot.register_handlers()
        logger.info("Bot handlers registered")
        
        await app_monitor.start_monitoring()
        logger.info("Monitoring started")
        
        await notification_scheduler.start()
        logger.info("Scheduler started")
        
        logger.info("Bot initialization complete - webhook setup skipped during startup")
        logger.info("Weather Bot application started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Weather Bot application...")
    
    try:
        await notification_scheduler.stop()
        logger.info("Scheduler stopped")
        
        await weather_api.close()
        logger.info("Weather API client closed")
        
        if settings.webhook_url:
            await weather_bot.bot.delete_webhook()
            logger.info("Webhook deleted")
        
        await weather_bot.bot.session.close()
        logger.info("Bot session closed")
        
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="Weather Bot",
    description="Telegram bot for daily weather notifications",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Weather Bot API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    try:
        status = await get_system_status()
        
        if status.get("status") == "healthy":
            return JSONResponse(
                status_code=200,
                content=status
            )
        else:
            return JSONResponse(
                status_code=503,
                content=status
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Record request start time for performance monitoring
        start_time = datetime.now()
        
        # Get update data
        update_data = await request.json()
        logger.info(f"Received webhook update: {update_data}")
        
        # Validate and fix update data before processing
        if "message" in update_data and "from" in update_data["message"]:
            from_user = update_data["message"]["from"]
            # Add missing is_bot field if not present
            if "is_bot" not in from_user:
                from_user["is_bot"] = False
                logger.debug("Added missing is_bot field to message.from")
        
        # Process update with better error handling
        try:
            await dp.feed_raw_update(weather_bot.bot, update_data)
            logger.info("Update processed successfully")
        except Exception as process_error:
            logger.error(f"Error processing update: {process_error}", exc_info=True)
            # Try to report the error but don't fail the webhook
            try:
                await app_monitor.log_error(process_error, "update_processing")
            except:
                pass
            # Don't raise here, just log and continue
        
        # Record response time
        response_time = (datetime.now() - start_time).total_seconds()
        try:
            app_monitor.performance.record_response_time(response_time)
            app_monitor.performance.increment_metric("requests_success")
        except Exception as monitor_error:
            logger.error(f"Monitoring error: {monitor_error}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        try:
            app_monitor.performance.increment_metric("requests_error")
            # Log error to monitoring
            await app_monitor.log_error(e, "webhook")
        except Exception as monitor_error:
            logger.error(f"Monitoring error in exception handler: {monitor_error}")
        
        # Return 200 to prevent Telegram from retrying
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": "Webhook processing failed"}
        )


@app.get("/status")
async def get_status():
    try:
        return await get_system_status()
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@app.get("/metrics")
async def get_metrics():
    try:
        return app_monitor.performance.get_metrics()
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@app.post("/admin/test-notification/{user_id}")
async def send_test_notification(user_id: int):
    try:
        from scheduler import send_manual_notification
        await send_manual_notification(user_id)
        return {"status": "success", "message": f"Test notification sent to user {user_id}"}
    except Exception as e:
        logger.error(f"Test notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/users-at-time/{time_str}")
async def get_users_at_time(time_str: str):
    try:
        from scheduler import get_users_with_notifications_at_time
        users = await get_users_with_notifications_at_time(time_str)
        return {
            "time": time_str,
            "user_count": len(users),
            "users": [
                {
                    "user_id": user.user_id,
                    "city": user.city,
                    "language": user.language,
                    "notifications_enabled": user.notifications_enabled
                }
                for user in users
            ]
        }
    except Exception as e:
        logger.error(f"Users at time error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/scheduler-status")
async def get_scheduler_status():
    try:
        from scheduler import schedule_status
        return await schedule_status()
    except Exception as e:
        logger.error(f"Scheduler status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/setup-webhook")
async def setup_webhook_endpoint():
    try:
        webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
        
        await weather_bot.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Deleted existing webhook")
        
        result = await weather_bot.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        if result:
            logger.info(f"Webhook set successfully to: {webhook_url}")
            
            webhook_info = await weather_bot.bot.get_webhook_info()
            
            return {
                "status": "success",
                "message": "Webhook set successfully",
                "webhook_url": webhook_info.url,
                "pending_updates": webhook_info.pending_update_count
            }
        else:
            return {
                "status": "error",
                "message": "Failed to set webhook"
            }
            
    except Exception as e:
        logger.error(f"Setup webhook error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    await app_monitor.log_error(exc, "global_handler", path=str(request.url))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development"
    )
