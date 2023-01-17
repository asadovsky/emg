"""Utilities for reading and writing data."""

import json
from datetime import datetime


def dt(unix_millis: int) -> datetime:
    return datetime.fromtimestamp(unix_millis / 1000.0)


def read_samples_and_labels(
    filename: str,
) -> tuple[list[tuple[datetime, float]], list[datetime]]:
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    updates = [json.loads(x) for x in lines]
    samples = [(dt(u["Time"]), u["Value"]) for u in updates if "Label" not in u]
    labels = [dt(u["Time"]) for u in updates if "Label" in u]
    return samples, labels
