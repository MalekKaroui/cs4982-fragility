import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("results/kaggle_summary.csv")

order = {"low": 0, "medium": 1, "high": 2}
df["order"] = df["stress_level"].map(order)
df = df.sort_values("order")

plt.figure(figsize=(7, 5))
plt.plot(df["stress_level"], df["mean_fragility"], marker="o", linewidth=2)
plt.ylabel("Mean Fragility Index")
plt.xlabel("Stress Level")
plt.title("Kaggle Operational Graph: Stress–Fragility Curve")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("kaggle_stress_curve.png", dpi=300)
plt.close()

print("Saved: kaggle_stress_curve.png")