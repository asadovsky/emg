"""Utilities for reading and writing data."""

import json
from datetime import datetime


def ms2dt(unix_millis: int) -> datetime:
    return datetime.fromtimestamp(unix_millis / 1000.0)


def dt2ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def read_samples_and_labels(
    filename: str,
) -> tuple[list[tuple[datetime, float]], list[datetime]]:
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    updates = [json.loads(x) for x in lines]
    samples = [(ms2dt(u["Time"]), u["Value"]) for u in updates if "Label" not in u]
    labels = [ms2dt(u["Time"]) for u in updates if "Label" in u]
    return samples, labels


def write_samples_and_labels(
    filename: str, samples: list[tuple[datetime, float]], labels: list[datetime]
) -> None:
    updates = []
    i = 0
    for t, v in samples:
        while i < len(labels) and labels[i] < t:
            updates.append({"Time": dt2ms(labels[i]), "Label": True})
            i += 1
        updates.append({"Time": dt2ms(t), "Value": v})
    for label in labels[i:]:
        updates.append({"Time": dt2ms(label), "Label": True})
    with open(filename, "w", encoding="utf-8") as f:
        for u in updates:
            json.dump(u, f, separators=(",", ":"))
            f.write("\n")
