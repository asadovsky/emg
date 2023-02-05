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


def clip(values: list[float], *, lo_p: float = 1, hi_p: float = 99) -> list[float]:
    lo = float(np.percentile(values, lo_p)) if lo_p > 0 else float("-inf")
    hi = float(np.percentile(values, hi_p)) if hi_p < 100 else float("inf")
    return [min(hi, max(lo, v)) for v in values]


def plot(
    ts: list[datetime],
    means: list[float],
    variances: list[float],
    mean_log_ratios: list[float],
    variance_log_ratios: list[float],
    labels: list[datetime],
    preds: list[datetime],
) -> None:
    _, axs = plt.subplots(4, 1, sharex=True, figsize=(20, 12))
    axs[0].plot(ts[-len(means) :], clip(means), color="y")
    axs[1].plot(ts[-len(variances) :], clip(variances, hi_p=90), color="y")
    axs[2].plot(ts[-len(mean_log_ratios) :], clip(mean_log_ratios), color="y")
    axs[3].plot(ts[-len(variance_log_ratios) :], clip(variance_log_ratios), color="y")
    for t in labels:
        for ax in axs:
            ax.axvline(x=t, color="r")
    for t in preds:
        for ax in axs:
            ax.axvline(x=t, color="g", linestyle=":")
    plt.show()


def run(filename: str, savefig: bool = False) -> None:
    samples, labels = data.read_samples_and_labels(filename)
    ts = [t for t, _ in samples]
    stats = StreamStats()
    preds = []
    for t, v in samples:
        stats.push(v)
        if stats.full() and stats.pred():
            preds.append(t)

    plot(
        ts,
        stats.means.values(),
        stats.variances.values(),
        stats.mean_log_ratios.values(),
        stats.variance_log_ratios.values(),
        labels,
        preds,
    )
    if savefig:
        plt.savefig(filename.replace(".jsonl", ".png"))
