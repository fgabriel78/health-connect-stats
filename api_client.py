import requests
import logging
from typing import Dict, Any, List, Union
from exceptions import FitbitAPIError

logger = logging.getLogger(__name__)

class FitbitClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.fitbit.com/1/user/-"
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code != 200:
            logger.error(f"API Error ({response.status_code}): {response.text}")
            raise FitbitAPIError(f"API Error: {response.text}", status_code=response.status_code)
        
        return response.json()

    def get_daily_steps(self, date_str: str = "today") -> int:
        """
        Fetches steps for a specific date (YYYY-MM-DD or 'today').
        """
        url = f"{self.base_url}/activities/date/{date_str}.json"
        logger.debug(f"Fetching daily steps from {url}")
        
        response = self.session.get(url)
        data = self._handle_response(response)
        
        summary = data.get("summary", {})
        steps = summary.get("steps", 0)
        return int(steps)

    def get_step_time_series(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetches step count time series for a date range.
        Dates should be in YYYY-MM-DD format.
        """
        url = f"{self.base_url}/activities/steps/date/{start_date}/{end_date}.json"
        logger.debug(f"Fetching step time series from {url}")
        
        response = self.session.get(url)
        data = self._handle_response(response)
        
        # Response format: {"activities-steps": [{"dateTime": "YYYY-MM-DD", "value": "1234"}, ...]}
        return data.get("activities-steps", [])
