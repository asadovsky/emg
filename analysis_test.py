"""Tests the analysis module."""

import unittest
from datetime import timedelta

import analysis
from analysis import dt


def compute_metrics(
    labels: list[int], preds: list[int], tol: int
) -> tuple[int, int, int]:
    return analysis.compute_metrics(
        [dt(x) for x in labels], [dt(x) for x in preds], timedelta(milliseconds=tol)
    )


class AnalysisTest(unittest.TestCase):
    def test_compute_metrics_zero_tolerance(self) -> None:
        self.assertEqual(compute_metrics([], [], 0), (0, 0, 0))
        self.assertEqual(compute_metrics([0], [], 0), (0, 0, 1))
        self.assertEqual(compute_metrics([], [0], 0), (0, 1, 0))
        self.assertEqual(compute_metrics([0], [0], 0), (1, 0, 0))
        self.assertEqual(compute_metrics([0], [0, 0], 0), (1, 0, 0))
        self.assertEqual(compute_metrics([0], [1], 0), (0, 1, 1))
        self.assertEqual(compute_metrics([1], [0], 0), (0, 1, 1))
        self.assertEqual(compute_metrics([0], [0, 1], 0), (1, 1, 0))
        self.assertEqual(compute_metrics([0, 1], [0], 0), (1, 0, 1))
        self.assertEqual(compute_metrics([0, 1], [0, 1], 0), (2, 0, 0))
        self.assertEqual(compute_metrics([0, 2], [0, 1], 0), (1, 1, 1))
        self.assertEqual(compute_metrics([2, 3], [0, 1], 0), (0, 2, 2))

    def test_compute_metrics_with_tolerance(self) -> None:
        self.assertEqual(compute_metrics([0], [100], 100), (1, 0, 0))
        self.assertEqual(compute_metrics([100], [0], 100), (1, 0, 0))
        self.assertEqual(compute_metrics([0], [0, 100], 100), (1, 0, 0))
        self.assertEqual(compute_metrics([100], [0, 100], 100), (1, 0, 0))
        self.assertEqual(compute_metrics([0, 200], [100], 100), (2, 0, 0))
