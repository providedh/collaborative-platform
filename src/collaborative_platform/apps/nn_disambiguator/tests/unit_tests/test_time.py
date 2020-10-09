from datetime import timedelta
from apps.nn_disambiguator.time import *
import pytest


class TestTime:
    def test_to_datetime(self):
        assert to_datetime("01.01.1970") == datetime(1970, 1, 1, 0, 0)
        yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        assert to_datetime("yesterday") == yesterday
        assert to_datetime("02_7_10") == datetime(2002, 7, 10, 0, 0)
        assert to_datetime("02_7_10 16_40") == datetime(2002, 7, 10, 16, 40)

    def test_days_apart(self):
        assert days_apart("now", "now") == 0
        assert days_apart("yesterday", "tomorrow") == 2
        assert days_apart("1.1.1970", datetime(2020, 8, 27)) == 18501
        assert days_apart("1.1.1970", "break") == max_days_apart

    def test_seconds_apart(self):
        assert seconds_apart("now", "now") == 0
        assert seconds_apart(datetime.now().time(), datetime.now() + timedelta(hours=7)) == 25200
        assert seconds_apart("12 p.m.", "6. p.m.") == 21600
        assert seconds_apart("13:37", "21:37") == 28800
