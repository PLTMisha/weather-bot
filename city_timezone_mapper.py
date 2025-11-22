import pytz
from datetime import datetime
from typing import Optional

def get_timezone_by_coordinates(lat: float, lon: float) -> str:
    """
    Get timezone by coordinates using a simple mapping approach.
    This is a basic implementation - for production, you might want to use
    a more sophisticated library like timezonefinder.
    """
    
    # Major timezone mappings based on approximate coordinate ranges
    timezone_mappings = [
        # Europe
        {"bounds": {"lat_min": 49.0, "lat_max": 61.0, "lon_min": -8.0, "lon_max": 2.0}, "timezone": "Europe/London"},  # UK & Ireland
        {"bounds": {"lat_min": 47.0, "lat_max": 55.0, "lon_min": 2.0, "lon_max": 15.0}, "timezone": "Europe/Paris"},   # France, Germany, etc
        {"bounds": {"lat_min": 35.0, "lat_max": 48.0, "lon_min": -10.0, "lon_max": 5.0}, "timezone": "Europe/Madrid"}, # Spain, Portugal
        {"bounds": {"lat_min": 35.0, "lat_max": 48.0, "lon_min": 5.0, "lon_max": 20.0}, "timezone": "Europe/Rome"},    # Italy, Switzerland
        {"bounds": {"lat_min": 44.0, "lat_max": 70.0, "lon_min": 15.0, "lon_max": 40.0}, "timezone": "Europe/Kiev"},   # Eastern Europe
        {"bounds": {"lat_min": 55.0, "lat_max": 70.0, "lon_min": 20.0, "lon_max": 180.0}, "timezone": "Europe/Moscow"}, # Russia (European part)
        
        # North America
        {"bounds": {"lat_min": 25.0, "lat_max": 50.0, "lon_min": -125.0, "lon_max": -117.0}, "timezone": "America/Los_Angeles"}, # US West Coast
        {"bounds": {"lat_min": 25.0, "lat_max": 50.0, "lon_min": -117.0, "lon_max": -104.0}, "timezone": "America/Denver"},      # US Mountain
        {"bounds": {"lat_min": 25.0, "lat_max": 50.0, "lon_min": -104.0, "lon_max": -80.0}, "timezone": "America/Chicago"},     # US Central
        {"bounds": {"lat_min": 25.0, "lat_max": 50.0, "lon_min": -80.0, "lon_max": -65.0}, "timezone": "America/New_York"},     # US East Coast
        {"bounds": {"lat_min": 45.0, "lat_max": 70.0, "lon_min": -140.0, "lon_max": -60.0}, "timezone": "America/Toronto"},     # Canada
        
        # Asia
        {"bounds": {"lat_min": 35.0, "lat_max": 55.0, "lon_min": 100.0, "lon_max": 135.0}, "timezone": "Asia/Shanghai"},   # China
        {"bounds": {"lat_min": 30.0, "lat_max": 46.0, "lon_min": 130.0, "lon_max": 146.0}, "timezone": "Asia/Tokyo"},     # Japan
        {"bounds": {"lat_min": 33.0, "lat_max": 43.0, "lon_min": 124.0, "lon_max": 132.0}, "timezone": "Asia/Seoul"},     # South Korea
        {"bounds": {"lat_min": 8.0, "lat_max": 37.0, "lon_min": 68.0, "lon_max": 97.0}, "timezone": "Asia/Kolkata"},      # India
        {"bounds": {"lat_min": 35.0, "lat_max": 42.0, "lon_min": 26.0, "lon_max": 45.0}, "timezone": "Europe/Istanbul"},  # Turkey
        
        # Australia & Oceania
        {"bounds": {"lat_min": -45.0, "lat_max": -10.0, "lon_min": 110.0, "lon_max": 155.0}, "timezone": "Australia/Sydney"}, # Australia East
        {"bounds": {"lat_min": -35.0, "lat_max": -15.0, "lon_min": 110.0, "lon_max": 130.0}, "timezone": "Australia/Perth"},   # Australia West
        
        # South America
        {"bounds": {"lat_min": -35.0, "lat_max": 12.0, "lon_min": -75.0, "lon_max": -35.0}, "timezone": "America/Sao_Paulo"}, # Brazil
        {"bounds": {"lat_min": -55.0, "lat_max": -20.0, "lon_min": -75.0, "lon_max": -53.0}, "timezone": "America/Argentina/Buenos_Aires"}, # Argentina
        
        # Africa
        {"bounds": {"lat_min": -35.0, "lat_max": 37.0, "lon_min": -20.0, "lon_max": 52.0}, "timezone": "Africa/Cairo"},    # Africa (general)
    ]
    
    # Check each mapping
    for mapping in timezone_mappings:
        bounds = mapping["bounds"]
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and 
            bounds["lon_min"] <= lon <= bounds["lon_max"]):
            return mapping["timezone"]
    
    # Default fallback based on longitude (rough approximation)
    if lon < -120:
        return "America/Los_Angeles"
    elif lon < -90:
        return "America/Chicago"
    elif lon < -60:
        return "America/New_York"
    elif lon < 15:
        return "Europe/London"
    elif lon < 45:
        return "Europe/Kiev"
    elif lon < 90:
        return "Asia/Kolkata"
    elif lon < 135:
        return "Asia/Shanghai"
    else:
        return "Asia/Tokyo"


def get_local_time_for_coordinates(lat: float, lon: float) -> datetime:
    """Get current local time for given coordinates"""
    timezone_str = get_timezone_by_coordinates(lat, lon)
    try:
        tz = pytz.timezone(timezone_str)
        utc_now = datetime.now(pytz.UTC)
        local_time = utc_now.astimezone(tz)
        return local_time
    except:
        # Fallback to UTC
        return datetime.now(pytz.UTC)


def format_local_time(lat: float, lon: float) -> tuple[str, str]:
    """Format local time for coordinates as date and time strings"""
    local_time = get_local_time_for_coordinates(lat, lon)
    date_str = local_time.strftime("%d.%m.%Y")
    time_str = local_time.strftime("%H:%M")
    return date_str, time_str
