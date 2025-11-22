import logging
import structlog
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import json

from config import settings
from database import DatabaseManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class BetterStackLogger:
    """BetterStack integration for logging and monitoring"""
    
    def __init__(self):
        self.token = settings.better_stack_token
        self.enabled = bool(self.token)
        
    async def log_event(self, level: str, message: str, **kwargs):
        """Log event to BetterStack"""
        if not self.enabled:
            return
            
        try:
            import httpx
            
            log_data = {
                "dt": datetime.utcnow().isoformat(),
                "level": level.upper(),
                "message": message,
                "source": "weather-bot",
                **kwargs
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://in.logs.betterstack.com/",
                    json=log_data,
                    headers=headers,
                    timeout=10
                )
                
        except Exception as e:
            # Don't let logging errors break the application
            print(f"BetterStack logging error: {e}")


class PerformanceMonitor:
    """Monitor application performance and metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "weather_api_calls": 0,
            "weather_api_errors": 0,
            "notifications_sent": 0,
            "notifications_failed": 0,
            "users_total": 0,
            "active_users_24h": 0
        }
        self.response_times = []
        
    def increment_metric(self, metric_name: str, value: int = 1):
        """Increment a metric counter"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def record_response_time(self, response_time: float):
        """Record response time for performance monitoring"""
        self.response_times.append(response_time)
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            **self.metrics,
            "avg_response_time": round(avg_response_time, 3),
            "response_times_count": len(self.response_times)
        }
    
    async def update_user_metrics(self):
        """Update user-related metrics from database"""
        try:
            from sqlalchemy import select, func, text
            from database import AsyncSessionLocal, User
            from datetime import datetime, timedelta
            
            async with AsyncSessionLocal() as session:
                # Total users
                total_users_result = await session.execute(select(func.count(User.user_id)))
                self.metrics["users_total"] = total_users_result.scalar() or 0
                
                # Active users in last 24 hours (users who interacted with bot)
                yesterday = datetime.now() - timedelta(days=1)
                active_users_query = select(func.count(func.distinct(User.user_id))).where(
                    User.updated_at >= yesterday
                )
                active_users_result = await session.execute(active_users_query)
                self.metrics["active_users_24h"] = active_users_result.scalar() or 0
                
        except Exception as e:
            logger.error("Failed to update user metrics", error=str(e))


class HealthChecker:
    """Health check functionality for monitoring"""
    
    def __init__(self):
        self.last_check = datetime.now()
        self.status = "healthy"
        self.checks = {}
    
    async def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            from database import AsyncSessionLocal
            from sqlalchemy import text
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            self.checks["database"] = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            return True
        except Exception as e:
            self.checks["database"] = {
                "status": "unhealthy", 
                "error": str(e), 
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    async def check_weather_api(self) -> bool:
        """Check weather API connectivity"""
        try:
            from weather_api import weather_api
            # Test with London coordinates
            result = await weather_api.get_weather_forecast(51.5074, -0.1278, "en")
            if result:
                self.checks["weather_api"] = {"status": "healthy", "timestamp": datetime.now().isoformat()}
                return True
            else:
                self.checks["weather_api"] = {
                    "status": "unhealthy", 
                    "error": "No data returned", 
                    "timestamp": datetime.now().isoformat()
                }
                return False
        except Exception as e:
            self.checks["weather_api"] = {
                "status": "unhealthy", 
                "error": str(e), 
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    async def check_scheduler(self) -> bool:
        """Check scheduler status"""
        try:
            from scheduler import notification_scheduler
            status = notification_scheduler.get_scheduler_status()
            if status.get("running"):
                self.checks["scheduler"] = {"status": "healthy", "timestamp": datetime.now().isoformat()}
                return True
            else:
                self.checks["scheduler"] = {
                    "status": "unhealthy", 
                    "error": "Scheduler not running", 
                    "timestamp": datetime.now().isoformat()
                }
                return False
        except Exception as e:
            self.checks["scheduler"] = {
                "status": "unhealthy", 
                "error": str(e), 
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        self.last_check = datetime.now()
        
        checks_results = await asyncio.gather(
            self.check_database(),
            self.check_weather_api(),
            self.check_scheduler(),
            return_exceptions=True
        )
        
        all_healthy = all(result is True for result in checks_results if not isinstance(result, Exception))
        self.status = "healthy" if all_healthy else "unhealthy"
        
        return {
            "status": self.status,
            "timestamp": self.last_check.isoformat(),
            "checks": self.checks
        }


class ApplicationMonitor:
    """Main monitoring class that coordinates all monitoring activities"""
    
    def __init__(self):
        self.better_stack = BetterStackLogger()
        self.performance = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.start_time = datetime.now()
    
    async def log_user_action(self, user_id: int, action: str, **kwargs):
        """Log user action with monitoring"""
        try:
            # Log to database
            await DatabaseManager.log_action(user_id, action, kwargs)
            
            # Log to BetterStack
            await self.better_stack.log_event(
                "info",
                f"User action: {action}",
                user_id=user_id,
                action=action,
                **kwargs
            )
            
            # Update metrics
            self.performance.increment_metric("requests_total")
            self.performance.increment_metric("requests_success")
            
        except Exception as e:
            logger.error("Failed to log user action", error=str(e), user_id=user_id, action=action)
            self.performance.increment_metric("requests_error")
    
    async def log_weather_api_call(self, success: bool, response_time: float, **kwargs):
        """Log weather API call"""
        try:
            self.performance.increment_metric("weather_api_calls")
            self.performance.record_response_time(response_time)
            
            if success:
                await self.better_stack.log_event(
                    "info",
                    "Weather API call successful",
                    response_time=response_time,
                    **kwargs
                )
            else:
                self.performance.increment_metric("weather_api_errors")
                await self.better_stack.log_event(
                    "error",
                    "Weather API call failed",
                    response_time=response_time,
                    **kwargs
                )
                
        except Exception as e:
            logger.error("Failed to log weather API call", error=str(e))
    
    async def log_notification_sent(self, user_id: int, success: bool, **kwargs):
        """Log notification sending"""
        try:
            if success:
                self.performance.increment_metric("notifications_sent")
                await self.better_stack.log_event(
                    "info",
                    "Notification sent successfully",
                    user_id=user_id,
                    **kwargs
                )
            else:
                self.performance.increment_metric("notifications_failed")
                await self.better_stack.log_event(
                    "error",
                    "Notification sending failed",
                    user_id=user_id,
                    **kwargs
                )
                
        except Exception as e:
            logger.error("Failed to log notification", error=str(e))
    
    async def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log application error"""
        try:
            await self.better_stack.log_event(
                "error",
                f"Application error in {context}: {str(error)}",
                error_type=type(error).__name__,
                context=context,
                **kwargs
            )
            
            logger.error("Application error", error=str(error), context=context, **kwargs)
            
        except Exception as e:
            logger.error("Failed to log error", error=str(e))
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Update user metrics
            await self.performance.update_user_metrics()
            
            # Run health checks
            health_status = await self.health_checker.run_health_checks()
            
            # Get performance metrics
            metrics = self.performance.get_metrics()
            
            uptime = datetime.now() - self.start_time
            
            return {
                "status": health_status["status"],
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_human": str(uptime),
                "health_checks": health_status["checks"],
                "metrics": metrics,
                "last_health_check": health_status["timestamp"],
                "environment": settings.environment
            }
            
        except Exception as e:
            logger.error("Failed to get system status", error=str(e))
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        try:
            # Log application startup
            await self.better_stack.log_event(
                "info",
                "Weather bot application started",
                environment=settings.environment,
                timestamp=self.start_time.isoformat()
            )
            
            logger.info("Monitoring system started")
            
        except Exception as e:
            logger.error("Failed to start monitoring", error=str(e))


# Global monitoring instance
app_monitor = ApplicationMonitor()


# Utility functions for easy access
async def log_user_action(user_id: int, action: str, **kwargs):
    """Log user action"""
    await app_monitor.log_user_action(user_id, action, **kwargs)


async def log_weather_api_call(success: bool, response_time: float, **kwargs):
    """Log weather API call"""
    await app_monitor.log_weather_api_call(success, response_time, **kwargs)


async def log_notification_sent(user_id: int, success: bool, **kwargs):
    """Log notification"""
    await app_monitor.log_notification_sent(user_id, success, **kwargs)


async def log_error(error: Exception, context: str = "", **kwargs):
    """Log error"""
    await app_monitor.log_error(error, context, **kwargs)


async def get_system_status():
    """Get system status"""
    return await app_monitor.get_system_status()
