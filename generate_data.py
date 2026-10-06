"""
Stage 1: DATA COLLECTION (prototype)
Creates ~50,000 realistic SAMPLE accident records (as stated in the PPT) so the
whole pipeline runs without downloading anything.

To use REAL data instead, download a Kaggle / data.gov.in road-accident CSV,
save it as data/raw_accidents.csv and skip this script (see README, "Real data").
"""
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 50_000
os.makedirs("data", exist_ok=True)

# state, city, lat, lon, relative weight
CITIES = [
    ("Karnataka", "Bengaluru", 12.97, 77.59, 12), ("Karnataka", "Mysuru", 12.30, 76.64, 3),
    ("Maharashtra", "Mumbai", 19.08, 72.88, 12), ("Maharashtra", "Pune", 18.52, 73.86, 7),
    ("Tamil Nadu", "Chennai", 13.08, 80.27, 10), ("Tamil Nadu", "Coimbatore", 11.02, 76.96, 4),
    ("Delhi", "New Delhi", 28.61, 77.21, 13), ("Telangana", "Hyderabad", 17.39, 78.49, 9),
    ("West Bengal", "Kolkata", 22.57, 88.36, 7), ("Gujarat", "Ahmedabad", 23.02, 72.57, 6),
    ("Rajasthan", "Jaipur", 26.91, 75.79, 5), ("Uttar Pradesh", "Lucknow", 26.85, 80.95, 7),
    ("Kerala", "Kochi", 9.93, 76.27, 4), ("Andhra Pradesh", "Visakhapatnam", 17.69, 83.22, 3),
]
w = np.array([c[4] for c in CITIES], float); w /= w.sum()
idx = rng.choice(len(CITIES), N, p=w)

dates = pd.to_datetime("2019-01-01") + pd.to_timedelta(rng.integers(0, 6 * 365, N), unit="D")
hour_p = np.array([1,1,1,1,1.5,2,3,4.5,5,4,3.5,3.5,4,3.5,3.5,4,5,6.5,7,6,4.5,3.5,2.5,1.5], float)
hours = rng.choice(24, N, p=hour_p / hour_p.sum())

causes = ["Speeding", "Signal jump", "Drunk driving", "Weather", "Poor road", "Other"]
cause = rng.choice(causes, N, p=[.38, .17, .14, .11, .10, .10])
severity = rng.choice(["Minor", "Serious", "Fatal"], N, p=[.52, .33, .15])
# drunk driving and speeding skew more severe
bump = np.isin(cause, ["Speeding", "Drunk driving"]) & (rng.random(N) < .12)
severity = np.where(bump & (severity == "Minor"), "Serious", severity)

weather = rng.choice(["Clear", "Rain", "Fog", "Cloudy"], N, p=[.58, .22, .08, .12])
weather = np.where(cause == "Weather", rng.choice(["Rain", "Fog"], N), weather)

df = pd.DataFrame({
    "accident_id": np.arange(1, N + 1),
    "date": dates.strftime("%Y-%m-%d"),
    "time": [f"{h:02d}:{m:02d}" for h, m in zip(hours, rng.integers(0, 60, N))],
    "state": [CITIES[i][0] for i in idx],
    "city": [CITIES[i][1] for i in idx],
    "latitude": [CITIES[i][2] + rng.normal(0, .06) for i in idx],
    "longitude": [CITIES[i][3] + rng.normal(0, .06) for i in idx],
    "weather": weather,
    "road_type": rng.choice(["Highway", "City road", "Rural road", "Junction"], N, p=[.30, .38, .17, .15]),
    "vehicle_type": rng.choice(["Two-wheeler", "Car", "Truck", "Bus", "Auto", "Pedestrian"], N, p=[.36, .24, .14, .07, .10, .09]),
    "cause": cause,
    "severity": severity,
})
df["casualties"] = np.select(
    [df.severity == "Fatal", df.severity == "Serious"],
    [rng.integers(1, 5, N), rng.integers(1, 4, N)], default=rng.integers(0, 2, N))

# make it realistically DIRTY so the cleaning stage has work to do
df.loc[rng.choice(N, 1500, replace=False), "weather"] = None
df.loc[rng.choice(N, 800, replace=False), "road_type"] = None
df.loc[rng.choice(N, 600, replace=False), "city"] = df["city"].str.upper()
df.loc[rng.choice(N, 400, replace=False), "cause"] = df["cause"].str.lower()
df = pd.concat([df, df.sample(700, random_state=1)], ignore_index=True)  # duplicates

df.to_csv("data/raw_accidents.csv", index=False)
print(f"Saved data/raw_accidents.csv  ({len(df):,} rows incl. deliberate dirt)")
