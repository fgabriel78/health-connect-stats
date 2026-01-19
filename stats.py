from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List

from api_client import FitbitClient

logger = logging.getLogger(__name__)

def calculate_stats(client: FitbitClient) -> Dict[str, Any]:
    """
    Orchestrates data fetching and statistics calculation.
    """
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    
    # 1. Get today's steps
    logger.info(f"Fetching data for today ({today_str})...")
    today_steps = client.get_daily_steps(today_str)
    
    # 2. Get data for the last 30 days
    yesterday = today - timedelta(days=1)
    date_30_days_ago = yesterday - timedelta(days=29) # Total 30 days including yesterday
    
    start_date_str = date_30_days_ago.strftime("%Y-%m-%d")
    end_date_str = yesterday.strftime("%Y-%m-%d")
    
    logger.info(f"Fetching historical data from {start_date_str} to {end_date_str}...")
    time_series = client.get_step_time_series(start_date_str, end_date_str)
    
    # Parse time series map for date-based lookup
    steps_by_date = {entry["dateTime"]: int(entry["value"]) for entry in time_series}
    
    # helper to generate date range
    daily_values: List[int] = []
    current_date = date_30_days_ago
    
    # Iterate through the expected 30 days
    while current_date <= yesterday:
        d_str = current_date.strftime("%Y-%m-%d")
        steps = steps_by_date.get(d_str, 0) # Default to 0 if no data for date
        daily_values.append(steps)
        current_date += timedelta(days=1)
        
    # Calculate averages
    # Weekly: Last 7 entries from the 30-day list
    last_7_days = daily_values[-7:]
    
    # Explicitly divide by 7 and 30 (or actual count if we changed logic, but here we forced the size)
    # This gives "Average steps per day over the last week/month" regardless of missing data holes.
    weekly_avg = sum(last_7_days) / 7
    monthly_avg = sum(daily_values) / 30
    
    return {
        "today_steps": today_steps,
        "weekly_avg": round(weekly_avg, 2),
        "monthly_avg": round(monthly_avg, 2),
        "days_counted_weekly": len(last_7_days),
        "days_counted_monthly": len(daily_values)
    }
