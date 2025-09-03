#!/usr/bin/env python3
"""
Test script to verify the scheduler now works at any minute
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import NotificationScheduler
from datetime import datetime

async def test_scheduler_jobs():
    """Test that scheduler creates jobs for every minute"""
    print("Testing scheduler job creation...")
    
    scheduler = NotificationScheduler()
    
    # Start scheduler to create jobs
    await scheduler.start()
    
    # Get all jobs
    jobs = scheduler.scheduler.get_jobs()
    
    # Filter notification jobs (exclude keep_alive job)
    notification_jobs = [job for job in jobs if job.id.startswith("notifications_")]
    
    print(f"Total notification jobs created: {len(notification_jobs)}")
    print(f"Expected: {24 * 60} (24 hours × 60 minutes)")
    
    # Check if we have jobs for every minute
    expected_jobs = 24 * 60  # 24 hours × 60 minutes
    
    if len(notification_jobs) == expected_jobs:
        print("✅ SUCCESS: Scheduler creates jobs for every minute!")
    else:
        print(f"❌ ERROR: Expected {expected_jobs} jobs, got {len(notification_jobs)}")
    
    # Show some example job times
    print("\nExample job times (first 10):")
    for i, job in enumerate(notification_jobs[:10]):
        print(f"  {job.id}: {job.name}")
    
    print("\nExample job times (last 10):")
    for job in notification_jobs[-10:]:
        print(f"  {job.id}: {job.name}")
    
    # Check specific minutes that weren't available before
    test_minutes = ["08:07", "14:23", "19:41", "22:59"]
    print(f"\nChecking availability of specific times that weren't available before:")
    
    for test_time in test_minutes:
        job_id = f"notifications_{test_time.replace(':', '_')}"
        job_exists = any(job.id == job_id for job in notification_jobs)
        status = "✅ Available" if job_exists else "❌ Not available"
        print(f"  {test_time}: {status}")
    
    # Stop scheduler
    await scheduler.stop()
    
    return len(notification_jobs) == expected_jobs

if __name__ == "__main__":
    success = asyncio.run(test_scheduler_jobs())
    if success:
        print("\n🎉 All tests passed! Scheduler now works at any minute.")
    else:
        print("\n❌ Tests failed. Please check the implementation.")
