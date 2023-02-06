"""Data labeling code."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from modeling import analysis, data
from modeling.stream_stats import StreamStats


def adjust_labels(
    ts: list[datetime], variance_log_ratios: list[float], labels: list[datetime]
) -> list[datetime]:
    res = []
    i = 0
    for label in labels:
        while i < len(ts) and label - ts[i] > timedelta(seconds=1):
            i += 1
        j = i
        while j < len(ts) and variance_log_ratios[j] < 2:
            j += 1
        if j < len(ts):
            res.append(ts[j])
    return res


def run(filename: str, *, write: bool = False) -> None:
    samples, labels = data.read_samples_and_labels(filename)
    ts = [t for t, _ in samples]
    stats = StreamStats()
    for _, v in samples:
        stats.push(v)

    variance_log_ratios = stats.variance_log_ratios.values()
    adjusted_labels = adjust_labels(
        ts[-len(variance_log_ratios) :], variance_log_ratios, labels
    )
    if write:
        data.write_samples_and_labels(
            filename.replace(".jsonl", ".adjusted.jsonl"), samples, adjusted_labels
        )

    analysis.plot(
        ts,
        stats.means.values(),
        stats.variances.values(),
        stats.mean_log_ratios.values(),
        variance_log_ratios,
        labels,
        adjusted_labels,
    )
    plt.show()
