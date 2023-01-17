"""Tests the data module."""

import unittest
from datetime import datetime

from modeling.data import dt2ms, ms2dt


class DataTest(unittest.TestCase):
    def test_ms2dt_dt2ms(self) -> None:
        ms = int(datetime.now().timestamp() * 1000)
        self.assertEqual(ms, dt2ms(ms2dt(ms)))
        dt = ms2dt(ms)
        self.assertEqual(dt, ms2dt(dt2ms(dt)))
