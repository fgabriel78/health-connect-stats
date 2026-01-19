import sys
import logging
from pydantic import ValidationError

from config import settings, Settings
from auth import FitbitAuth
from api_client import FitbitClient
from stats import calculate_stats
from exceptions import ConfigError, HealthConnectError

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Google Health Connect Stats (via Fitbit)...")
    
    try:
        # Settings are already loaded by import, but we could re-load or validate if needed
        # In this pattern, 'settings' is a global instance from config.py
        logger.debug(f"Loaded configuration for Client ID: {settings.client_id}")
        
    except ValidationError as e:
        logger.critical(f"Configuration Invalid: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to load configuration: {e}")
        sys.exit(1)
        
    try:
        auth = FitbitAuth(settings)
        # Check if we have credentials or need to auth
        # Note: get_token will trigger auth flow if needed
        token = auth.get_token()
        
        client = FitbitClient(token)
        
        logger.info("Fetching data and calculating statistics...")
        stats = calculate_stats(client)
        
        print("\n" + "="*30)
        print(" GOOGLE HEALTH CONNECT STATS")
        print(" (via Fitbit API)")
        print("="*30)
        print(f"Today's Steps:      {stats['today_steps']}")
        print(f"Weekly Average:     {stats['weekly_avg']} (Last {stats['days_counted_weekly']} days)")
        print(f"Monthly Average:    {stats['monthly_avg']} (Last {stats['days_counted_monthly']} days)")
        print("="*30 + "\n")
        
        logger.info("Done.")
        
    except HealthConnectError as e:
        logger.error(f"Application Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
