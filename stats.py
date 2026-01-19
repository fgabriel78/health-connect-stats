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
    
    # Parse time series
    daily_values: List[int] = []
    for entry in time_series:
        daily_values.append(int(entry["value"]))
        
    # Calculate averages
    # Weekly: Last 7 entries
    last_7_days = daily_values[-7:] if len(daily_values) >= 7 else daily_values
    weekly_avg = sum(last_7_days) / len(last_7_days) if last_7_days else 0
    
    # Monthly: Last 30 entries (or however many we got)
    monthly_avg = sum(daily_values) / len(daily_values) if daily_values else 0
    
    return {
        "today_steps": today_steps,
        "weekly_avg": round(weekly_avg, 2),
        "monthly_avg": round(monthly_avg, 2),
        "days_counted_weekly": len(last_7_days),
        "days_counted_monthly": len(daily_values)
    }
