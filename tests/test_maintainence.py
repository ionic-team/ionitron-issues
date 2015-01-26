# python -m unittest discover

import unittest
from tasks import maintainence as m
from datetime import datetime


class TestMaintainance(unittest.TestCase):

    def test_should_run_daily_maintainence(self):
        r = m.should_run_daily_maintainence(min_refresh_seconds=60, last_update_str='')
        self.assertEquals(r, True)

        now = datetime(2000, 1, 1, 1, 0, 0)
        r = m.should_run_daily_maintainence(min_refresh_seconds=60, last_update_str='2000-01-01 00:00:00', now=now)
        self.assertEquals(r, True)

        now = datetime(2000, 1, 1, 0, 0, 59)
        r = m.should_run_daily_maintainence(min_refresh_seconds=60, last_update_str='2000-01-01 00:00:00', now=now)
        self.assertEquals(r, False)
