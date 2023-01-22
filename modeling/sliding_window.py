"""Defines SlidingWindow."""


class SlidingWindow:
    """Maintains a sliding window of values and stats."""

    def __init__(self, window_size: int) -> None:
        self._window_size: int = window_size
        self._values: list[float] = [0.0] * self._window_size
        self._i: int = 0
        self._n: int = 0
        self._mean: float = 0.0
        self._variance: float = 0.0

    def full(self) -> bool:
        return self._n == self._window_size

    def get(self, i: int) -> float:
        assert -self._window_size < i <= 0
        return self._values[(self._i + i + self._window_size) % self._window_size]

    def mean(self) -> float:
        return self._mean

    def variance(self) -> float:
        return self._variance

    def push(self, value: float) -> None:
        self._i = (self._i + 1) % self._window_size
        old_mean = self._mean
        if not self.full():
            self._n += 1
            self._mean += (value - self._mean) / self._n
            self._variance += (value - self._mean) * (value - old_mean)
            if self.full():
                self._variance /= self._n - 1
        else:
            old_value = self.get(0)
            self._mean += (value - old_value) / self._n
            self._variance += (
                (value - old_value)
                * (value - self._mean + old_value - old_mean)
                / (self._n - 1)
            )
        self._values[self._i] = value
