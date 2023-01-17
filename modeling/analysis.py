"""Data analysis code."""

import math
from collections import deque
from collections.abc import Collection
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from modeling import data


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


def compute_moments(values: Collection[float]) -> tuple[float, float]:
    mean, variance = 0, 0
    for i, v in enumerate(values):
        # Welford's algorithm.
        old_mean = mean
        mean += (v - mean) / (i + 1)
        variance += (v - mean) * (v - old_mean)
    variance /= len(values) - 1
    return mean, variance


def clip(
    values: list[float], *, lo: float = float("-inf"), hi: float = float("inf")
) -> list[float]:
    return [min(hi, max(lo, v)) for v in values]


def mk_trailing_moments(values: list[float], w: int) -> tuple[list[float], list[float]]:
    """Returns trailing (means, variances)."""
    means: list[float] = [0] * (w - 1)
    variances: list[float] = [0] * (w - 1)

    r = deque(values[:w], maxlen=w)
    mean, variance = compute_moments(r)
    means.append(mean)
    variances.append(variance)
    for v in values[w:]:
        # https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
        old_v = r[0]
        old_mean = mean
        mean += (v - old_v) / w
        variance += (v - old_v) * (v - mean + old_v - old_mean) / (w - 1)
        r.append(v)
        means.append(mean)
        variances.append(variance)

    assert len(means) == len(variances) == len(values)
    return means, variances


def mk_smoothed_values(values: list[float], w: int) -> list[float]:
    means, _ = mk_trailing_moments(values, w)
    return [means[w - 1]] * (w - 1) + means[w - 1 :]


def mk_mean_log_ratios(mean: float, trailing_means: list[float], w: int) -> list[float]:
    res: list[float] = [0] * (w - 1)
    for v in trailing_means[w - 1 :]:
        res.append(math.log(v) - math.log(mean))
    assert len(res) == len(trailing_means)
    return res


def mk_preds(
    ts: list[datetime], variances: list[float], mean_log_ratios: list[float], w: int
) -> list[datetime]:
    res = []
    n = 3
    for i in range(len(variances)):
        if (
            i >= (n + 1) * w - 1
            and variances[i] > 5
            and mean_log_ratios[i] > 0.01
            and all(variances[i - (j + 1) * w] < 1 for j in range(n))
        ):
            res.append(ts[i])
    return res


def run() -> None:
    samples, labels = data.read_samples_and_labels(
        "../data/julie_3m_stable.adjusted.jsonl"
    )
    ts = [t for t, _ in samples]
    vs = [v for _, v in samples]
    smoothed_values = mk_smoothed_values(vs, 5)
    w = 20
    means, variances = mk_trailing_moments(smoothed_values, w)
    mean_log_ratios = mk_mean_log_ratios(means[w - 1], means, w)
    preds = mk_preds(ts, variances, mean_log_ratios, w)

    _, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(20, 9))
    ax1.plot(ts, clip(smoothed_values, lo=280, hi=320), color="y")
    ax2.plot(ts, clip(variances, hi=10), color="y")
    ax3.plot(ts, mean_log_ratios, color="y")
    for t in labels:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="r")
    for t in preds:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="g", linestyle=":")
    plt.show()
