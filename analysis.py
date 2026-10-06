"""
Stage 4: DATA ANALYSIS (EDA) -> prints findings and saves PNG charts in charts/
Run:  python analysis.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import pandas as pd

os.makedirs("charts", exist_ok=True)
df = pd.read_csv("data/accidents_clean.csv", parse_dates=["date"])
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

print("Total accidents :", f"{len(df):,}")
print("Fatal accidents :", f"{(df.severity == 'Fatal').sum():,}")
print("\nBy year\n", df.groupby("year").size())
print("\nCause share (%)\n", (df.cause.value_counts(normalize=True) * 100).round(1))
print("\nSeverity share (%)\n", (df.severity.value_counts(normalize=True) * 100).round(1))
print("\nTop 5 cities\n", df.city.value_counts().head(5))
print("\nPeak hours\n", df.hour.value_counts().head(3))
print("\nDeadliest cause (fatal rate %)\n",
      (df.assign(f=df.severity == "Fatal").groupby("cause").f.mean() * 100).round(1).sort_values(ascending=False))

fig, ax = plt.subplots(2, 2, figsize=(13, 9))
df.groupby("year").size().plot(marker="o", ax=ax[0, 0], title="Accidents by Year", color="#2b7a9b")
(df.cause.value_counts(normalize=True) * 100).sort_values().plot.barh(ax=ax[0, 1], title="Accidents by Cause (%)", color="#f5a623")
df.severity.value_counts().plot.pie(ax=ax[1, 0], autopct="%1.0f%%", title="Severity", wedgeprops=dict(width=.45))
df.groupby("hour").size().plot.bar(ax=ax[1, 1], title="Accidents by Hour", color="#2b7a9b")
for a in ax.ravel():
    a.set_ylabel("")
plt.tight_layout()
plt.savefig("charts/summary.png", dpi=130)
print("\nSaved charts/summary.png")
