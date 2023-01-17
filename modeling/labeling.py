"""Data labeling code."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from modeling import data
from modeling.analysis import clip, mk_smoothed_values, mk_trailing_moments


def adjust_labels(
    ts: list[datetime], variances: list[float], labels: list[datetime]
) -> list[datetime]:
    res = []
    i = 0
    for label in labels:
        while i < len(ts) and label - ts[i] > timedelta(seconds=1):
            i += 1
        j = i
        while j < len(ts) and variances[j] < 5:
            j += 1
        res.append(ts[j])
    assert len(res) == len(labels)
    return res


def run(write: bool = False) -> None:
    samples, labels = data.read_samples_and_labels("../data/julie_3m_stable.jsonl")
    ts = [t for t, _ in samples]
    vs = [v for _, v in samples]
    smoothed_values = mk_smoothed_values(vs, 5)
    _, variances = mk_trailing_moments(smoothed_values, 20)
    adjusted_labels = adjust_labels(ts, variances, labels)
    if write:
        data.write_samples_and_labels(
            "../data/julie_3m_stable.adjusted.jsonl", samples, adjusted_labels
        )

    _, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(20, 6))
    ax1.plot(ts, clip(smoothed_values, lo=280, hi=320), color="y")
    ax2.plot(ts, clip(variances, hi=10), color="y")
    for t in labels:
        for ax in [ax1, ax2]:
            ax.axvline(x=t, color="r")
    for t in adjusted_labels:
        for ax in [ax1, ax2]:
            ax.axvline(x=t, color="g")
    plt.show()