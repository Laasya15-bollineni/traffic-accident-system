"""
Stage 2: DATA CLEANING & PREPROCESSING  +  Stage 3: DATA STORAGE
 - remove duplicates, handle missing values, standardize text/dates
 - saves data/accidents_clean.csv and a SQLite DB (data/accidents.db)
"""
import sqlite3
import pandas as pd

RAW, CLEAN, DB = "data/raw_accidents.csv", "data/accidents_clean.csv", "data/accidents.db"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # duplicates (ignore the id column)
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "accident_id"])

    # standardize text columns
    for c in ["state", "city", "weather", "road_type", "vehicle_type", "cause", "severity"]:
        if c in df:
            df[c] = df[c].astype("string").str.strip().str.title()

    # missing values: categorical -> "Unknown", critical fields -> drop
    for c in ["weather", "road_type", "vehicle_type", "cause"]:
        if c in df:
            df[c] = df[c].fillna("Unknown")
    df = df.dropna(subset=["date", "severity", "latitude", "longitude"])

    # dates & derived time features
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["hour"] = pd.to_datetime(df["time"], format="%H:%M", errors="coerce").dt.hour.fillna(0).astype(int)
    df["year"] = df.date.dt.year
    df["month"] = df.date.dt.month
    df["day_of_week"] = df.date.dt.day_name()
    df["casualties"] = pd.to_numeric(df["casualties"], errors="coerce").fillna(0).astype(int)

    print(f"Cleaned: {n0:,} -> {len(df):,} rows ({n0 - len(df):,} removed)")
    return df.reset_index(drop=True)


if __name__ == "__main__":
    out = clean(pd.read_csv(RAW))
    out.to_csv(CLEAN, index=False)
    with sqlite3.connect(DB) as con:
        out.to_sql("accidents", con, if_exists="replace", index=False)
    print(f"Saved {CLEAN} and SQLite table 'accidents' in {DB}")
