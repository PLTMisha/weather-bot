#!/usr/bin/env python3
"""
Test script to verify that the bot now shows city local time instead of user timezone
"""

import asyncio
import os
from datetime import datetime
import pytz
from city_timezone_mapper import get_timezone_by_coordinates, format_local_time

async def test_city_timezone_functionality():
    """Test the city timezone functionality"""
    print("🧪 Testing City Timezone Functionality")
    print("=" * 50)
    
    # Test cases: different cities with their coordinates
    test_cities = [
        {
            "name": "London, UK",
            "lat": 51.5074,
            "lon": -0.1278,
            "expected_tz": "Europe/London"
        },
        {
            "name": "Kiev, Ukraine", 
            "lat": 50.4501,
            "lon": 30.5234,
            "expected_tz": "Europe/Kiev"
        },
        {
            "name": "New York, USA",
            "lat": 40.7128,
            "lon": -74.0060,
            "expected_tz": "America/New_York"
        },
        {
            "name": "Tokyo, Japan",
            "lat": 35.6762,
            "lon": 139.6503,
            "expected_tz": "Asia/Tokyo"
        }
    ]
    
    current_utc = datetime.now(pytz.UTC)
    print(f"Current UTC time: {current_utc.strftime('%H:%M')}")
    print()
    
    for city in test_cities:
        print(f"🌍 Testing {city['name']}:")
        print(f"   Coordinates: ({city['lat']}, {city['lon']})")
        
        # Test timezone detection
        detected_tz = get_timezone_by_coordinates(city['lat'], city['lon'])
        print(f"   Detected timezone: {detected_tz}")
        print(f"   Expected timezone: {city['expected_tz']}")
        
        # Test local time formatting
        local_date, local_time = format_local_time(city['lat'], city['lon'])
        print(f"   Local date: {local_date}")
        print(f"   Local time: {local_time}")
        
        # Calculate expected time manually for verification
        tz = pytz.timezone(detected_tz)
        local_dt = current_utc.astimezone(tz)
        expected_time = local_dt.strftime('%H:%M')
        expected_date = local_dt.strftime('%d.%m.%Y')
        print(f"   Expected date: {expected_date}")
        print(f"   Expected time: {expected_time}")
        
        # Check if they match
        if local_time == expected_time and local_date == expected_date:
            print("   ✅ PASS - Date and time match!")
        else:
            print("   ❌ FAIL - Date or time don't match!")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_city_timezone_functionality())
