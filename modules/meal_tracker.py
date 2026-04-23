import difflib
from datetime import date
import pandas as pd
import streamlit as st

CSV_PATH = "data/nutrients.csv"

DAILY_GOALS = {
    "Calories": 2000,
    "Protein": 50,
    "Fat": 65,
    "Carbs": 300,
    "Fiber": 25,
}

@st.cache_data(show_spinner=False)
def load_db():
    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.strip() for c in df.columns]
        for col in ["Calories", "Protein", "Fat", "Sat.Fat", "Fiber", "Carbs", "Grams"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        if "Food" in df.columns:
            df["Food"] = df["Food"].astype(str).str.strip()
        if "Measure" not in df.columns:
            df["Measure"] = ""
        df["Measure"] = df["Measure"].fillna("").astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

def search_food(query, top_n=5):
    db = load_db()
    if db.empty or not query:
        return pd.DataFrame()

    q = query.lower().strip()
    res = db[db["Food"].str.lower().str.contains(q, na=False, regex=False)].copy()

    if res.empty:
        matches = difflib.get_close_matches(query, db["Food"].tolist(), n=top_n, cutoff=0.45)
        res = db[db["Food"].isin(matches)].copy()

    return res.head(top_n).reset_index(drop=True)

def get_food_nutrition(food):
    df = load_db()
    row = df[df["Food"] == food]
    if row.empty:
        return None

    r = row.iloc[0]
    return {
        "food": r["Food"],
        "measure": r.get("Measure", ""),
        "grams": float(r.get("Grams", 100) or 100),
        "calories": float(r.get("Calories", 0)),
        "protein": float(r.get("Protein", 0)),
        "fat": float(r.get("Fat", 0)),
        "carbs": float(r.get("Carbs", 0)),
        "fiber": float(r.get("Fiber", 0)),
    }

def _today():
    return str(date.today())

def get_today_log():
    return st.session_state.get("meal_log", {}).get(_today(), [])

def add_meal(food_info, quantity_g=None):
    if "meal_log" not in st.session_state:
        st.session_state.meal_log = {}

    today = _today()
    if today not in st.session_state.meal_log:
        st.session_state.meal_log[today] = []

    ref = food_info["grams"] or 100
    qty = quantity_g if quantity_g else ref
    scale = qty / ref if ref else 1

    entry = {
        "food": food_info["food"],
        "measure": food_info.get("measure", ""),
        "grams": round(qty, 1),
        "calories": round(food_info["calories"] * scale, 1),
        "protein": round(food_info["protein"] * scale, 1),
        "fat": round(food_info["fat"] * scale, 1),
        "carbs": round(food_info["carbs"] * scale, 1),
        "fiber": round(food_info["fiber"] * scale, 1),
    }
    st.session_state.meal_log[today].append(entry)
    return entry

def remove_meal(index):
    today = _today()
    log = st.session_state.get("meal_log", {}).get(today, [])
    if 0 <= index < len(log):
        st.session_state.meal_log[today].pop(index)

def get_daily_totals():
    totals = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "fiber": 0.0}
    for e in get_today_log():
        for k in totals:
            totals[k] += e.get(k, 0.0)
    return {k: round(v, 1) for k, v in totals.items()}

def clear_today_log():
    if "meal_log" not in st.session_state:
        st.session_state.meal_log = {}
    st.session_state.meal_log[_today()] = []
