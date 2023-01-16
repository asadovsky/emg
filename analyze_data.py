import datetime
import json

import matplotlib.pyplot as plt

with open("data.jsonl") as f:
    lines = f.readlines()

updates = [json.loads(v) for v in lines]
times = [
    datetime.datetime.fromtimestamp(u["Time"] / 1000.0)
    for u in updates
    if u["Value"] != 0
]
values = [u["Value"] for u in updates if u["Value"] != 0]

k = 5
smoothed_values = []
for i in range(k, len(values) - k):
    smoothed_values.append(sum(values[i - k : i + k + 1]) / (2 * k + 1))

plt.plot(times[k:-k], smoothed_values, "r")
plt.plot(times, values, "b")
plt.show()
