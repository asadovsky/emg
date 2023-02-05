"""Defines SlidingWindow."""


class SlidingWindow:
    """Maintains a sliding window of values and stats."""

    def __init__(self, window_size: int, track_stats: bool) -> None:
        self._window_size: int = window_size
        self._track_stats: bool = track_stats
        self._values: list[float] = []
        self._n: int = 0
        self._mean: float = 0.0
        self._variance: float = 0.0

    def values(self) -> list[float]:
        return self._values

    def size(self) -> int:
        return self._n

    def full(self) -> bool:
        return self._n == self._window_size

    def get(self, i: int) -> float:
        assert -self._n < i <= 0
        return self._values[i - 1]

    def mean(self) -> float:
        return self._mean

    def variance(self) -> float:
        return self._variance

    def push(self, value: float) -> None:
        if not self._track_stats:
            if not self.full():
                self._n += 1
        else:
            old_mean = self._mean
            if not self.full():
                # Welford's algorithm.
                self._n += 1
                self._mean += (value - self._mean) / self._n
                self._variance += (value - self._mean) * (value - old_mean)
                if self.full():
                    self._variance /= self._n - 1
            else:
                # https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
                old_value = self.get(1 - self._window_size)
                self._mean += (value - old_value) / self._n
                self._variance += (
                    (value - old_value)
                    * (value - self._mean + old_value - old_mean)
                    / (self._n - 1)
                )
        self._values.append(value)
