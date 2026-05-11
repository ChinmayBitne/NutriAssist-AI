"""
meal_tracker.py
Handles everything related to the meal log:
  - Load and search the nutrition CSV database
  - Log meals to session state (keyed by today's date)
  - Calculate daily macro totals
  - Remove entries from the log

Updated to support quantity by grams OR count/servings using the food's Measure.
Compatible with the original function names/API.
"""

import difflib
import re
from datetime import date

import pandas as pd
import streamlit as st

CSV_PATH = "data/Final_nutrients_data.csv"

# Default daily goals (customisable)
DAILY_GOALS = {
    "Calories": 2000,
    "Protein": 50,
    "Fat": 65,
    "Carbs": 300,
    "Fiber": 25,
}

NUMERIC_COLUMNS = [
    "Calories", "Protein", "Fat", "Sat.Fat", "Fiber", "Carbs", "Grams",
    "Free Sugar (g)", "Sodium (mg)", "Calcium (mg)", "Iron (mg)",
    "Vitamin C (mg)", "Folate (µg)",
]

COUNT_WORDS = {
    "piece", "pieces", "pc", "pcs", "chapati", "roti", "egg", "eggs", "idli",
    "dosa", "dosai", "paratha", "parotta", "naan", "slice", "slices", "cup", "cups",
    "bowl", "bowls", "serving", "servings", "roll", "rolls", "cookie", "cookies",
    "sandwich", "sandwiches", "patty", "patties", "muffin", "muffins",
}


def _clean_measure_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _infer_quantity_mode(measure: str) -> str:
    """
    Return 'grams' if the measure looks weight-based, else 'count'.
    Examples:
      '100 g' -> grams
      '1 chapati' -> count
      '1 cup' -> count
      '2 pieces' -> count
    """
    m = _clean_measure_text(measure)
    if not m:
        return "grams"

    if re.search(r"\b(g|gm|gms|gram|grams|kg|ml|l|oz)\b", m):
        return "grams"

    tokens = set(re.findall(r"[a-zA-Z]+", m))
    if tokens & COUNT_WORDS:
        return "count"

    if re.search(r"^\d+(\.\d+)?$", m):
        return "count"

    return "count"


def _extract_measure_count(measure: str) -> float:
    """
    Extract count/servings from measure text.
    Examples:
      '1 chapati' -> 1.0
      '2 pieces' -> 2.0
      '1/2 cup' -> 0.5
      '' -> 1.0
    """
    m = _clean_measure_text(measure)
    if not m:
        return 1.0

    frac = re.match(r"^(\d+)\s*/\s*(\d+)", m)
    if frac:
        num, den = frac.groups()
        den = float(den)
        return float(num) / den if den else 1.0

    mixed = re.match(r"^(\d+)\s+(\d+)\s*/\s*(\d+)", m)
    if mixed:
        whole, num, den = mixed.groups()
        den = float(den)
        return float(whole) + (float(num) / den if den else 0.0)

    dec = re.match(r"^(\d+(?:\.\d+)?)", m)
    if dec:
        return float(dec.group(1))

    return 1.0


@st.cache_data(show_spinner=False)
def load_nutrition_db() -> pd.DataFrame:
    """Load nutrients.csv. Returns empty DataFrame if file not found."""
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.strip() for c in df.columns]

        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if "Measure" not in df.columns:
            df["Measure"] = ""
        df["Measure"] = df["Measure"].fillna("").astype(str).str.strip()

        if "Food" in df.columns:
            df["Food"] = df["Food"].fillna("").astype(str).str.strip()
            df = df[df["Food"] != ""].copy()

        return df.reset_index(drop=True)
    except FileNotFoundError:
        return pd.DataFrame()


def search_food(query: str, top_n: int = 6) -> pd.DataFrame:
    """
    Search the database for food items matching the query.
    First tries substring match; falls back to fuzzy matching.
    Returns rows, preserving Measure so the UI can show count-based foods too.
    """
    db = load_nutrition_db()
    if db.empty or not query:
        return pd.DataFrame()

    q = query.lower().strip()

    mask = db["Food"].str.lower().str.contains(q, na=False, regex=False)
    results = db[mask].copy()

    if results.empty:
        food_list = db["Food"].tolist()
        close = difflib.get_close_matches(query, food_list, n=top_n, cutoff=0.40)
        if close:
            results = db[db["Food"].isin(close)].copy()

    # Prefer rows that have a non-empty Measure and more nutrition info.
    if not results.empty:
        results["_measure_len"] = results["Measure"].astype(str).str.len()
        score_cols = [c for c in ["Calories", "Protein", "Fat", "Carbs", "Fiber", "Grams"] if c in results.columns]
        results["_score"] = results[score_cols].notna().sum(axis=1) if score_cols else 0
        results = results.sort_values(["_score", "_measure_len"], ascending=False)
        results = results.drop(columns=[c for c in ["_measure_len", "_score"] if c in results.columns])

    return results.head(top_n).reset_index(drop=True)


def get_food_nutrition(food_name: str) -> dict | None:
    """Return a nutrition dict for the best-matching food item."""
    results = search_food(food_name, top_n=1)
    if results.empty:
        return None

    row = results.iloc[0]
    measure = str(row.get("Measure", "") or "")
    quantity_mode = _infer_quantity_mode(measure)
    ref_count = _extract_measure_count(measure) if quantity_mode == "count" else None

    return {
        "food": row["Food"],
        "measure": measure,
        "calories": float(row.get("Calories", 0)),
        "protein": float(row.get("Protein", 0)),
        "fat": float(row.get("Fat", 0)),
        "carbs": float(row.get("Carbs", 0)),
        "fiber": float(row.get("Fiber", 0)),
        "sat_fat": float(row.get("Sat.Fat", 0)),
        "grams": float(row.get("Grams", 100)),
        "quantity_mode": quantity_mode,   # 'grams' or 'count'
        "ref_count": ref_count,           # e.g. 1 chapati -> 1.0
    }


def _today() -> str:
    return str(date.today())


def get_today_log() -> list[dict]:
    """Return today's list of logged meal entries."""
    return st.session_state.get("meal_log", {}).get(_today(), [])


def add_meal(
        food_info, 
        quantity_g=None, 
        quantity_count=None,
    ) -> dict:
    """
    Log a meal.

    Usage:
      - For weight-based foods, pass quantity_g.
      - For count-based foods (e.g. chapati), pass quantity_count.
      - If neither is passed, uses the reference amount from the database.

    Keeps the old quantity_g API working for backward compatibility.
    Returns the logged entry dict.
    """
    if "meal_log" not in st.session_state:
        st.session_state.meal_log = {}

    today = str(date.today())
    if today not in st.session_state.meal_log:
        st.session_state.meal_log[today] = []

    ref_g = food_info.get("grams", 100) or 100

    # Detect mode
    if quantity_count is not None:
        scale = quantity_count
        grams = ref_g * scale
        quantity = quantity_count
        unit = "count"
    else:
        qty = quantity_g if quantity_g else ref_g
        scale = qty / ref_g
        grams = qty
        quantity = qty
        unit = "grams"

    entry = {
        "food": food_info["food"],
        "quantity": quantity,
        "quantity_unit": unit,
        "grams": round(grams, 1),
        "calories": round(food_info["calories"] * scale, 1),
        "protein": round(food_info["protein"] * scale, 1),
        "fat": round(food_info["fat"] * scale, 1),
        "carbs": round(food_info["carbs"] * scale, 1),
        "fiber": round(food_info["fiber"] * scale, 1),
    }

    st.session_state.meal_log[today].append(entry)
    return entry


def remove_meal(index: int) -> None:
    """Remove an entry from today's log by index."""
    today = _today()
    log = st.session_state.get("meal_log", {}).get(today, [])
    if 0 <= index < len(log):
        st.session_state.meal_log[today].pop(index)


def get_daily_totals() -> dict:
    """Sum up all macros logged today."""
    totals = {k: 0.0 for k in ["calories", "protein", "fat", "carbs", "fiber"]}
    for entry in get_today_log():
        for key in totals:
            totals[key] += entry.get(key, 0.0)
    return {k: round(v, 1) for k, v in totals.items()}


def clear_today_log() -> None:
    today = _today()
    if "meal_log" in st.session_state and today in st.session_state.meal_log:
        st.session_state.meal_log[today] = []
