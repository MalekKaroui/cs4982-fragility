import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("results/kaggle_summary.csv")

# sort stress order
order = {"low": 0, "medium": 1, "high": 2}
df["order"] = df["stress_level"].map(order)
df = df.sort_values("order")

plt.figure(figsize=(7, 5))
plt.bar(df["stress_level"], df["mean_fragility"], color=["#3498db", "#f39c12", "#e74c3c"])
plt.ylabel("Mean Fragility Index")
plt.xlabel("Stress Level")
plt.title("Kaggle Operational Graph: Mean Fragility by Stress Scenario")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("figures/comparison/kaggle_mean_fragility.png", dpi=300)
plt.close()

print("Saved: figures/comparison/kaggle_mean_fragility.png")