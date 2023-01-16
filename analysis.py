import json
from datetime import datetime, timedelta

import matplotlib.pyplot as plt


def dt(unix_millis: int) -> datetime:
    return datetime.fromtimestamp(unix_millis / 1000.0)


def read_values_and_labels(
    filename: str,
) -> tuple[list[tuple[datetime, float]], list[datetime]]:
    with open(filename) as f:
        lines = f.readlines()
    updates = [json.loads(x) for x in lines]
    values = [(dt(u["Time"]), u["Value"]) for u in updates if "Label" not in u]
    labels = [dt(u["Time"]) for u in updates if "Label" in u]
    return values, labels


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


def plot_smoothed_values():
    values, _ = read_values_and_labels("data.jsonl")
    ts = [t for t, _ in values]
    vs = [v for _, v in values]

    k = 5
    smoothed_vs = []
    for i in range(k, len(vs) - k):
        smoothed_vs.append(sum(vs[i - k : i + k + 1]) / (2 * k + 1))

    plt.plot(ts[k:-k], smoothed_vs, "r")
    plt.plot(ts, vs, "b")
    plt.show()
