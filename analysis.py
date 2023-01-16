import json
from collections import deque
from datetime import datetime, timedelta

import matplotlib.pyplot as plt


def dt(unix_millis: int) -> datetime:
    return datetime.fromtimestamp(unix_millis / 1000.0)


def read_samples_and_labels(
    filename: str,
) -> tuple[list[tuple[datetime, float]], list[datetime]]:
    with open(filename) as f:
        lines = f.readlines()
    updates = [json.loads(x) for x in lines]
    samples = [(dt(u["Time"]), u["Value"]) for u in updates if "Label" not in u]
    labels = [dt(u["Time"]) for u in updates if "Label" in u]
    return samples, labels


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


def mk_smoothed_values(values: list[float], window_size: int) -> list[float]:
    w = window_size
    res: list[float] = []
    for i in range(w, len(values) - w):
        res.append(sum(values[i - w : i + w + 1]) / (2 * w + 1))
    res = [res[0]] * w + res + [res[-1]] * w
    assert len(res) == len(values)
    return res


def mk_moments(
    values: list[float], window_size: int
) -> tuple[list[float], list[float], list[float]]:
    """Returns (means, variances, sigma ratios)."""
    w = window_size
    means: list[float] = [0] * w
    variances: list[float] = [0] * w
    sigma_ratios: list[float] = [0] * w

    r = deque(maxlen=w)
    n: int = 0
    mean: float = 0
    variance: float = 0

    for v in values:
        if n == w:
            means.append(mean)
            variances.append(variance)
            sigma_ratios.append((v - mean) / (variance**0.5))
        old_mean = mean
        if n < w:
            # Welford's algorithm.
            n += 1
            mean += (v - mean) / n
            variance += (v - mean) * (v - old_mean)
            if n == w:
                variance /= w - 1
        else:
            # https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
            old_v = r[0]
            mean += (v - old_v) / w
            variance += (v - old_v) * (v - mean + old_v - old_mean) / (w - 1)
        r.append(v)

    assert len(means) == len(variances) == len(sigma_ratios) == len(values)
    return means, variances, sigma_ratios


def clip(
    values: list[float], *, lo: float = float("-inf"), hi: float = float("inf")
) -> list[float]:
    return [min(hi, max(lo, v)) for v in values]


def plot_samples():
    samples, labels = read_samples_and_labels("data/julie_3m_stable.jsonl")
    ts = [t for t, _ in samples]
    vs = [v for _, v in samples]
    smoothed_values = mk_smoothed_values(vs, 5)
    _, variances, sigma_ratios = mk_moments(smoothed_values, 50)
    preds = [ts[i] for i, v in enumerate(sigma_ratios) if v > 3]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    fig.set_size_inches(20, 10)
    ax1.plot(ts, clip(smoothed_values, lo=280, hi=320), color="y")
    ax2.plot(ts, variances, color="y")
    ax3.plot(ts, sigma_ratios, color="y")
    ax3.axhline(y=0, color="k", linestyle=":")
    for t in labels:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="r")
    for t in preds:
        for ax in [ax1, ax2, ax3]:
            ax.axvline(x=t, color="g", linestyle=":")
    plt.show()
