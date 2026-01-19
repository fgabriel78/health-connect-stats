import unittest
from stats import calculate_stats
from datetime import datetime, timedelta

class MockClient:
    def __init__(self, daily_steps=1000, time_series=[]):
        self.daily_steps = daily_steps
        self.time_series = time_series
        self.daily_steps_calls = []
        self.time_series_calls = []

    def get_daily_steps(self, date_str):
        self.daily_steps_calls.append(date_str)
        return self.daily_steps

    def get_step_time_series(self, start_date, end_date):
        self.time_series_calls.append((start_date, end_date))
        return self.time_series

class TestStats(unittest.TestCase):
    def test_calculate_stats_basic(self):
        # Mock data: 7 days of 1000 steps
        time_series = [{"dateTime": "2023-01-01", "value": "1000"} for _ in range(7)]
        client = MockClient(daily_steps=500, time_series=time_series)
        
        stats = calculate_stats(client)
        
        self.assertEqual(stats["today_steps"], 500)
        self.assertEqual(stats["weekly_avg"], 1000.0)
        self.assertEqual(stats["monthly_avg"], 1000.0)
        self.assertEqual(stats["days_counted_weekly"], 7)
        self.assertEqual(stats["days_counted_monthly"], 7)

    def test_calculate_stats_empty_history(self):
        client = MockClient(daily_steps=0, time_series=[])
        
        stats = calculate_stats(client)
        
        self.assertEqual(stats["today_steps"], 0)
        self.assertEqual(stats["weekly_avg"], 0)
        self.assertEqual(stats["monthly_avg"], 0)

    def test_calculate_stats_partial_week(self):
        # Mock data: 3 days of 1000 steps
        time_series = [{"dateTime": "2023-01-01", "value": "1000"} for _ in range(3)]
        client = MockClient(time_series=time_series)
        
        stats = calculate_stats(client)
        
        self.assertEqual(stats["weekly_avg"], 1000.0) # Average of available days
        self.assertEqual(stats["days_counted_weekly"], 3)

    def test_calculate_stats_varied_data(self):
        # Mock data: 10 days with values 0, 100, 200, ... 900
        values = [i * 100 for i in range(10)]
        time_series = [{"dateTime": f"2023-01-{i+1:02d}", "value": str(v)} for i, v in enumerate(values)]
        client = MockClient(time_series=time_series)
        
        stats = calculate_stats(client)
        
        # Monthly avg: sum(0..900) / 10 = 4500 / 10 = 450
        self.assertEqual(stats["monthly_avg"], 450.0)
        
        # Weekly avg: last 7 days (300..900)
        # sum(300..900) = 4200. 4200 / 7 = 600
        self.assertEqual(stats["weekly_avg"], 600.0)

if __name__ == '__main__':
    unittest.main()
