import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("results/fragility_kaggle_medium.csv")
topk = df.sort_values("normalized_fragility", ascending=False).head(10)

plt.figure(figsize=(10, 5))
plt.bar(topk["node_id"], topk["normalized_fragility"], color="salmon", edgecolor="black")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.ylabel("Normalized Fragility")
plt.title("Top-10 Most Fragile Nodes — Kaggle Operational Graph (Medium Stress)")
plt.tight_layout()
plt.savefig("figures/comparison/kaggle_topk_medium.png", dpi=300)
plt.close()

print("Saved: figures/comparison/kaggle_topk_medium.png")