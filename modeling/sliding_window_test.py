"""Tests SlidingWindow."""

import unittest

import numpy as np

from modeling.sliding_window import SlidingWindow

_WINDOW_SIZE = 10


class SlidingWindowTest(unittest.TestCase):
    def test_simple(self) -> None:
        sw = SlidingWindow(_WINDOW_SIZE, True)
        values = np.arange(0, 1, 1 / _WINDOW_SIZE / 5)
        means = [
            np.mean(values[i : i + _WINDOW_SIZE])
            for i in range(len(values) - _WINDOW_SIZE + 1)
        ]
        variances = [
            np.var(values[i : i + _WINDOW_SIZE], ddof=1)
            for i in range(len(values) - _WINDOW_SIZE + 1)
        ]
        for i, v in enumerate(values):
            self.assertEqual(min(i, _WINDOW_SIZE), sw.size())
            self.assertEqual(i >= _WINDOW_SIZE, sw.full())
            sw.push(v)
            if i >= _WINDOW_SIZE - 1:
                self.assertAlmostEqual(sw.mean(), float(means[i - (_WINDOW_SIZE - 1)]))
                self.assertAlmostEqual(
                    sw.variance(), float(variances[i - (_WINDOW_SIZE - 1)])
                )
        self.assertEqual(sw.values(), list(values))
        self.assertEqual(sw.get(0), values[-1])
        self.assertEqual(sw.get(1 - _WINDOW_SIZE), values[-_WINDOW_SIZE])
        with self.assertRaises(AssertionError):
            sw.get(1)
        with self.assertRaises(AssertionError):
            sw.get(-_WINDOW_SIZE)
