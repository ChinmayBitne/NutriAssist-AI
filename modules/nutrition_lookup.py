from __future__ import annotations

import difflib
from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/nutrients.csv")

USEFUL_COLUMNS = [
    "Food", "Measure", "Grams", "Calories", "Protein", "Fat", "Sat.Fat",
    "Fiber", "Carbs", "Free Sugar (g)", "Sodium (mg)", "Calcium (mg)",
    "Iron (mg)", "Vitamin C (mg)", "Folate (µg)"
]

def load_db() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]

    for col in USEFUL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    for col in [c for c in USEFUL_COLUMNS if c not in ["Food", "Measure"]]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Food"] = df["Food"].astype(str).str.strip()
    df["Measure"] = df["Measure"].fillna("").astype(str).str.strip()

    df = df[df["Food"] != ""].copy()
    return df[USEFUL_COLUMNS].reset_index(drop=True)

def search_food(query: str, top_n: int = 3) -> pd.DataFrame:
    db = load_db()
    if db.empty or not query:
        return pd.DataFrame()

    q = query.lower().strip()
    contains = db[db["Food"].str.lower().str.contains(q, na=False, regex=False)].copy()

    if not contains.empty:
        return contains.head(top_n).reset_index(drop=True)

    close = difflib.get_close_matches(query, db["Food"].tolist(), n=top_n, cutoff=0.45)
    if close:
        return db[db["Food"].isin(close)].head(top_n).reset_index(drop=True)

    return pd.DataFrame()

def _fmt(v):
    if pd.isna(v):
        return None
    v = float(v)
    return int(v) if v.is_integer() else round(v, 1)

def build_food_context(query: str) -> str:
    matches = search_food(query, top_n=2)
    if matches.empty:
        return ""

    lines = []
    for _, row in matches.iterrows():
        food = row.get("Food", "")
        measure = row.get("Measure", "")
        facts = []
        for col, label, unit in [
            ("Calories", "calories", ""),
            ("Protein", "protein", "g"),
            ("Fat", "fat", "g"),
            ("Sat.Fat", "sat fat", "g"),
            ("Fiber", "fiber", "g"),
            ("Carbs", "carbs", "g"),
            ("Free Sugar (g)", "free sugar", "g"),
            ("Sodium (mg)", "sodium", "mg"),
            ("Calcium (mg)", "calcium", "mg"),
            ("Iron (mg)", "iron", "mg"),
            ("Vitamin C (mg)", "vitamin C", "mg"),
            ("Folate (µg)", "folate", "µg"),
        ]:
            val = _fmt(row.get(col))
            if val is not None:
                facts.append(f"{label}: {val}{unit}")
        lines.append(f"{food} | measure: {measure} | " + ", ".join(facts))

    return "\n".join(lines)
