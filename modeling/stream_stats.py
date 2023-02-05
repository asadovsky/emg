"""Defines StreamStats."""

import math

from modeling.sliding_window import SlidingWindow

_STATS_WINDOW_SIZE = 20  # 200ms
_SLIDING_WINDOW_SIZE = 300  # 3s


class StreamStats:
    """Maintains various stats over a stream of values."""

    def __init__(self) -> None:
        # Computed over a sliding window of raw values.
        self.stats: SlidingWindow = SlidingWindow(_STATS_WINDOW_SIZE, True)
        # Means and variances from `stats`.
        self.means: SlidingWindow = SlidingWindow(_SLIDING_WINDOW_SIZE, False)
        self.variances: SlidingWindow = SlidingWindow(_SLIDING_WINDOW_SIZE, False)
        # Current-vs-recent mean and variance log ratios.
        self.mean_log_ratios: SlidingWindow = SlidingWindow(_SLIDING_WINDOW_SIZE, False)
        self.variance_log_ratios: SlidingWindow = SlidingWindow(
            _SLIDING_WINDOW_SIZE, False
        )

    def full(self) -> bool:
        return (
            self.stats.full()
            and self.means.full()
            and self.variances.full()
            and self.mean_log_ratios.full()
            and self.variance_log_ratios.full()
        )

    def push(self, value: float) -> None:
        self.stats.push(value)
        if not self.stats.full():
            return
        mean, variance = self.stats.mean(), self.stats.variance()
        self.means.push(mean)
        self.variances.push(variance)
        i = -100  # -1s
        if self.means.size() <= -i:
            return
        self.mean_log_ratios.push(math.log(mean) - math.log(self.means.get(i)))
        self.variance_log_ratios.push(
            math.log(variance) - math.log(self.variances.get(i))
        )

    def pred(self) -> bool:
        assert self.full()
        # Mean spike at 0s.
        if self.mean_log_ratios.get(0) < 0.02:
            return False
        # Mean dip in [-1s, 0s].
        i = 0
        while True:
            if i < -100:
                return False
            if self.mean_log_ratios.get(i) < -0.02:
                break
            i -= 1
        # No mean spike in [-2s, dip].
        while i > -200:
            if self.mean_log_ratios.get(i) > 0.02:
                return False
            i -= 1
        return True
