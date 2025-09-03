import asyncio
from monitoring import app_monitor

async def test_health_components():
    print("=== Testing Health Components ===")
    
    # Test database
    print("\n1. Testing database...")
    try:
        db_result = await app_monitor.health_checker.check_database()
        print(f"Database: {'✅ OK' if db_result else '❌ FAIL'}")
        print(f"Details: {app_monitor.health_checker.checks.get('database', {})}")
    except Exception as e:
        print(f"Database: ❌ ERROR - {e}")
    
    # Test weather API
    print("\n2. Testing weather API...")
    try:
        weather_result = await app_monitor.health_checker.check_weather_api()
        print(f"Weather API: {'✅ OK' if weather_result else '❌ FAIL'}")
        print(f"Details: {app_monitor.health_checker.checks.get('weather_api', {})}")
    except Exception as e:
        print(f"Weather API: ❌ ERROR - {e}")
    
    # Test scheduler
    print("\n3. Testing scheduler...")
    try:
        scheduler_result = await app_monitor.health_checker.check_scheduler()
        print(f"Scheduler: {'✅ OK' if scheduler_result else '❌ FAIL'}")
        print(f"Details: {app_monitor.health_checker.checks.get('scheduler', {})}")
    except Exception as e:
        print(f"Scheduler: ❌ ERROR - {e}")
    
    # Test full system status
    print("\n4. Testing full system status...")
    try:
        status = await app_monitor.get_system_status()
        print(f"Overall status: {status.get('status', 'unknown')}")
        print(f"Health checks: {status.get('health_checks', {})}")
    except Exception as e:
        print(f"System status: ❌ ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(test_health_components())
