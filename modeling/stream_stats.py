"""Defines StreamStats."""

import math

from modeling.sliding_window import SlidingWindow

_SMOOTHED_WINDOW_SIZE = 5  # 50ms
_TRAILING_WINDOW_SIZE = 20  # 200ms
_NUM_WINDOWS = 3


class StreamStats:
    """Maintains various stats over a stream of values."""

    def __init__(self) -> None:
        # Computed over a sliding window of raw values.
        self.raw_stats: SlidingWindow = SlidingWindow(_SMOOTHED_WINDOW_SIZE)
        # Computed over a sliding window of smoothed values.
        self.smoothed_stats: SlidingWindow = SlidingWindow(_TRAILING_WINDOW_SIZE)
        self.smoothed_values: list[float] = []
        # Means from `smoothed_stats`.
        self.means: list[float] = []
        # Variances from `smoothed_stats`.
        self.variances: list[float] = []
        # The first value added to `means`.
        self.initial_mean: float = 0.0
        # Current-vs-initial mean log ratios.
        self.mean_log_ratios: list[float] = []

    def full(self) -> bool:
        return (
            self.raw_stats.full()
            and self.smoothed_stats.full()
            and len(self.means) >= 1
            and len(self.variances) >= _NUM_WINDOWS * _TRAILING_WINDOW_SIZE + 1
            and len(self.mean_log_ratios) >= 1
        )

    def push(self, value: float) -> None:
        self.raw_stats.push(value)
        if not self.raw_stats.full():
            return
        self.smoothed_stats.push(self.raw_stats.mean())
        self.smoothed_values.append(self.raw_stats.mean())
        if not self.smoothed_stats.full():
            return
        if len(self.means) == 0:
            self.initial_mean = self.smoothed_stats.mean()
        self.means.append(self.smoothed_stats.mean())
        self.variances.append(self.smoothed_stats.variance())
        self.mean_log_ratios.append(
            math.log(self.smoothed_stats.mean()) - math.log(self.initial_mean)
        )

    def pred(self) -> bool:
        assert self.full()
        if self.variances[-1] < 5 or self.mean_log_ratios[-1] < 0.01:
            return False
        for i in range(_NUM_WINDOWS):
            if self.variances[-(i + 1) * _TRAILING_WINDOW_SIZE - 1] > 1:
                return False
        return True
