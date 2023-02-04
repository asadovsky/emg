"""Data analysis code."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np

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


def clip(values: list[float], *, lo_p: float = 0, hi_p: float = 100) -> list[float]:
    lo = float(np.percentile(values, lo_p)) if lo_p > 0 else float("-inf")
    hi = float(np.percentile(values, hi_p)) if hi_p < 100 else float("inf")
    return [min(hi, max(lo, v)) for v in values]


def run(filename: str, savefig: bool = False) -> None:
    samples, labels = data.read_samples_and_labels(filename)
    ts = [t for t, _ in samples]
    stats = StreamStats()
    preds = []
    for t, v in samples:
        stats.push(v)
        if stats.full() and stats.pred():
            preds.append(t)

    smoothed_values = stats.smoothed_stats.values()
    variances = stats.variances.values()
    mean_log_ratios = stats.mean_log_ratios.values()

    _, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(20, 9))
    ax1.plot(
        ts[-len(smoothed_values) :],
        clip(smoothed_values, lo_p=1, hi_p=99),
        color="y",
    )
    ax2.plot(ts[-len(variances) :], clip(variances, hi_p=90), color="y")
    ax3.plot(ts[-len(mean_log_ratios) :], mean_log_ratios, color="y")
    for t in labels:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="r")
    for t in preds:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="g", linestyle=":")
    if savefig:
        plt.savefig(filename.replace(".jsonl", ".png"))
    plt.show()
