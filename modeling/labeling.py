"""Data labeling code."""

import matplotlib.pyplot as plt

from modeling import data
from modeling.analysis import clip, mk_smoothed_values


def run():
    samples, labels = data.read_samples_and_labels("../data/julie_3m_stable.jsonl")
    ts = [t for t, _ in samples]
    vs = [v for _, v in samples]
    smoothed_values = mk_smoothed_values(vs, 5)

    _ = plt.figure(figsize=(20, 5))
    plt.plot(ts, clip(smoothed_values, lo=280, hi=320), color="y")
    for t in labels:
        plt.axvline(x=t, color="r")
    plt.show()
