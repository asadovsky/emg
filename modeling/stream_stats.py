"""Defines StreamStats."""

import math

from modeling.sliding_window import SlidingWindow

_SMOOTHED_WINDOW_SIZE = 5  # 50ms
_TRAILING_WINDOW_SIZE = 20  # 200ms
_NUM_WINDOWS = 10


class StreamStats:
    """Maintains various stats over a stream of values."""

    def __init__(self) -> None:
        # Computed over a sliding window of raw values.
        self.raw_stats: SlidingWindow = SlidingWindow(_SMOOTHED_WINDOW_SIZE, True)
        # Computed over a sliding window of smoothed values.
        self.smoothed_stats: SlidingWindow = SlidingWindow(_TRAILING_WINDOW_SIZE, True)
        # Means from `smoothed_stats`.
        self.means: SlidingWindow = SlidingWindow(1, False)
        # Variances from `smoothed_stats`.
        self.variances: SlidingWindow = SlidingWindow(
            _NUM_WINDOWS * _TRAILING_WINDOW_SIZE, False
        )
        # The first value added to `means`.
        self.initial_mean: float = 0.0
        # Current-vs-initial mean log ratios.
        self.mean_log_ratios: SlidingWindow = SlidingWindow(1, False)

    def full(self) -> bool:
        return (
            self.raw_stats.full()
            and self.smoothed_stats.full()
            and self.means.full()
            and self.variances.full()
            and self.mean_log_ratios.full()
        )

    def push(self, value: float) -> None:
        self.raw_stats.push(value)
        if not self.raw_stats.full():
            return
        self.smoothed_stats.push(self.raw_stats.mean())
        if not self.smoothed_stats.full():
            return
        if self.means.size() == 0:
            self.initial_mean = self.smoothed_stats.mean()
        self.means.push(self.smoothed_stats.mean())
        self.variances.push(self.smoothed_stats.variance())
        self.mean_log_ratios.push(
            math.log(self.smoothed_stats.mean()) - math.log(self.initial_mean)
        )

    def pred(self) -> bool:
        assert self.full()
        if self.variances.get(0) < 2000 or self.mean_log_ratios.get(0) > -0.005:
            return False
        for i in range(40, 120):
            if self.variances.get(-i) > 750:
                return False
        return True
