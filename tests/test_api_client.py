import unittest
from unittest.mock import patch, MagicMock
from api_client import FitbitClient
from exceptions import FitbitAPIError

class TestFitbitClient(unittest.TestCase):
    def setUp(self):
        self.access_token = "fake_token"
        self.client = FitbitClient(self.access_token)

    def test_headers_set_on_init(self):
        # Accessing session headers to verify they are set correctly
        self.assertEqual(self.client.session.headers["Authorization"], "Bearer fake_token")
        self.assertEqual(self.client.session.headers["Accept"], "application/json")

    @patch('requests.Session.get')
    def test_get_daily_steps_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "summary": {
                "steps": 1234
            }
        }
        mock_get.return_value = mock_response

        steps = self.client.get_daily_steps("2023-01-01")
        
        self.assertEqual(steps, 1234)
        mock_get.assert_called_with(
            "https://api.fitbit.com/1/user/-/activities/date/2023-01-01.json"
        )

    @patch('requests.Session.get')
    def test_get_daily_steps_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        # Expect FitbitAPIError instead of generic Exception
        with self.assertRaises(FitbitAPIError) as cm:
            self.client.get_daily_steps()
        
        self.assertIn("API Error", str(cm.exception))
        self.assertEqual(cm.exception.status_code, 401)

    @patch('requests.Session.get')
    def test_get_step_time_series_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_data = [{"dateTime": "2023-01-01", "value": "100"}]
        mock_response.json.return_value = {"activities-steps": mock_data}
        mock_get.return_value = mock_response

        data = self.client.get_step_time_series("2023-01-01", "2023-01-02")
        
        self.assertEqual(data, mock_data)
        mock_get.assert_called_with(
            "https://api.fitbit.com/1/user/-/activities/steps/date/2023-01-01/2023-01-02.json"
        )

if __name__ == '__main__':
    unittest.main()
