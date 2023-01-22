"""Data analysis code."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from modeling import data
from modeling.stream_stats import StreamStats


def compute_metrics(
    labels: list[datetime], preds: list[datetime], tol: timedelta
) -> tuple[int, int, int]:
    """Returns (true positive, false positive, false negative) counts.

    Assumes `labels` and `preds` are sorted. Each label is counted as either one true
    positive or one false negative.
    """
    tp, fp, fn = 0, 0, 0
    # Count true positives and false negatives.
    i = 0
    for label in labels:
        while i < len(preds):
            pred = preds[i]
            if pred < label - tol:
                i += 1
                continue
            elif pred > label + tol:
                fn += 1
            else:
                tp += 1
            break
        if i == len(preds):
            fn += 1
    # Count false positives.
    i = 0
    for pred in preds:
        while i < len(labels):
            label = labels[i]
            if label < pred - tol:
                i += 1
                continue
            elif label > pred + tol:
                fp += 1
            break
        if i == len(labels):
            fp += 1
    assert tp + fn == len(labels)
    assert fp <= len(preds)
    return tp, fp, fn


def clip(
    values: list[float], *, lo: float = float("-inf"), hi: float = float("inf")
) -> list[float]:
    return [min(hi, max(lo, v)) for v in values]


def run() -> None:
    samples, labels = data.read_samples_and_labels(
        "../data/julie_3m_stable.adjusted.jsonl"
    )
    ts = [t for t, _ in samples]
    stats = StreamStats()
    preds = []
    for t, v in samples:
        stats.push(v)
        if stats.full() and stats.pred():
            preds.append(t)

    _, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(20, 9))
    ax1.plot(
        ts[-len(stats.smoothed_values) :],
        clip(stats.smoothed_values, lo=280, hi=320),
        color="y",
    )
    ax2.plot(ts[-len(stats.variances) :], clip(stats.variances, hi=10), color="y")
    ax3.plot(ts[-len(stats.mean_log_ratios) :], stats.mean_log_ratios, color="y")
    for t in labels:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="r")
    for t in preds:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="g", linestyle=":")
    plt.show()
