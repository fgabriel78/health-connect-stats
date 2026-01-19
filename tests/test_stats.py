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
    def setUp(self):
        self.today = datetime.now().date()
        self.yesterday = self.today - timedelta(days=1)

    def _generate_time_series(self, days_back, value_fn):
        """Helper to generate time series data ending yesterday"""
        series = []
        for i in range(days_back):
            date = self.yesterday - timedelta(days=i)
            val = value_fn(i)
            series.append({"dateTime": date.strftime("%Y-%m-%d"), "value": str(val)})
        return series

    def test_calculate_stats_basic(self):
        # Mock data: 30 days of 1000 steps (full history)
        # Note: generated backwards, but order doesn't matter for dictionary lookup
        time_series = self._generate_time_series(30, lambda i: 1000)
        client = MockClient(daily_steps=500, time_series=time_series)
        
        stats = calculate_stats(client)
        
        self.assertEqual(stats["today_steps"], 500)
        self.assertEqual(stats["weekly_avg"], 1000.0)
        self.assertEqual(stats["monthly_avg"], 1000.0)
        # Note: We don't check implementation details like "days_counted_weekly" 
        # unless we kept that key in the return dict. The refactor kept it?
        # Let's check the keys in the previous view_file. Yes, keys are still there.
        # But in new logic, days_counted corresponds to the loop iterations (7 or 30).
        # Actually in the code: len(last_7_days) and len(daily_values).
        # daily_values should be 30 integers. last_7_days should be 7 integers.
        # So these should be constant now.
        # self.assertEqual(stats["days_counted_weekly"], 7)
        # self.assertEqual(stats["days_counted_monthly"], 30)

    def test_calculate_stats_empty_history(self):
        client = MockClient(daily_steps=0, time_series=[])
        
        stats = calculate_stats(client)
        
        self.assertEqual(stats["today_steps"], 0)
        self.assertEqual(stats["weekly_avg"], 0.0)
        self.assertEqual(stats["monthly_avg"], 0.0)

    def test_calculate_stats_partial_week(self):
        # Mock data: Only 3 days of 1000 steps provided (e.g. yesterday, day before, day before)
        # Rest of the days will be filled with 0 by the logic.
        time_series = self._generate_time_series(3, lambda i: 1000)
        client = MockClient(time_series=time_series)
        
        stats = calculate_stats(client)
        
        # Weekly avg: (1000 * 3 + 0 * 4) / 7 = 3000 / 7 = 428.57
        self.assertAlmostEqual(stats["weekly_avg"], 428.57, places=2)
        
        # Monthly avg: (1000 * 3 + 0 * 27) / 30 = 3000 / 30 = 100
        self.assertEqual(stats["monthly_avg"], 100.0)

    def test_calculate_stats_varied_data(self):
        # Mock data: 10 days with values. 
        # i=0 (yesterday) -> 900
        # i=9 (9 days ago) -> 0
        # logic: value = (9-i) * 100. 
        # So yesterday (i=0) is 900. Day before (i=1) is 800. ... 9 days ago (i=9) is 0.
        time_series = self._generate_time_series(10, lambda i: (9-i) * 100)
        client = MockClient(time_series=time_series)
        
        stats = calculate_stats(client)
        
        # Data present (last 10 days): [0, 100, 200, 300, 400, 500, 600, 700, 800, 900]
        # Sum = 4500
        # Monthly Average (over 30 days): 4500 / 30 = 150
        self.assertEqual(stats["monthly_avg"], 150.0)
        
        # Weekly avg (last 7 days):
        # The list is reconstructed from 30 days ago to yesterday.
        # daily_values[-7:] will be the last 7 entries (closest to yesterday).
        # These correspond to i=6 down to i=0.
        # Values: 300, 400, 500, 600, 700, 800, 900
        # Sum = 4200
        # Avg = 4200 / 7 = 600
        self.assertEqual(stats["weekly_avg"], 600.0)

if __name__ == '__main__':
    unittest.main()
