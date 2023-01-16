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


def mk_sigma_ratios(values: list[float], window_size: int) -> list[float]:
    w = window_size
    res: list[float] = [0] * w

    r = deque(maxlen=w)
    n: int = 0
    mean: float = 0
    variance: float = 0

    for v in values:
        if n == w:
            res.append(abs(v - mean) / (variance**0.5))
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

    assert len(res) == len(values)
    return res


def clip(
    values: list[float], *, lo: float = float("-inf"), hi: float = float("inf")
) -> list[float]:
    return [min(hi, max(lo, v)) for v in values]


def plot_samples():
    samples, labels = read_samples_and_labels("data/julie_3m_electrodes.jsonl")
    ts = [t for t, _ in samples]
    plt.plot(ts, [v for _, v in samples], "y")
    for label in labels:
        plt.axvline(x=label, color="r", linestyle="--")
    plt.show()
