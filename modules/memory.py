"""
memory.py
Extracts and stores lightweight session profile details from user messages.
"""

from __future__ import annotations

import re

_CONDITIONS = {
    "diabetes", "pre-diabetes", "prediabetes", "hypertension", "high blood pressure",
    "heart disease", "cardiovascular disease", "celiac", "celiac disease",
    "lactose intolerant", "lactose intolerance", "gluten free", "gluten intolerance",
    "vegan", "vegetarian", "pescatarian", "obesity", "overweight", "underweight",
    "anemia", "anaemia", "gout", "ibs", "crohn", "kidney disease", "kidney failure",
    "high cholesterol", "high triglycerides", "thyroid", "hypothyroid", "hyperthyroid",
    "pcos", "insulin resistance", "fatty liver", "liver disease", "allergy", "allergies",
}

_GOALS = {
    "lose weight": "weight loss",
    "weight loss": "weight loss",
    "losing weight": "weight loss",
    "gain muscle": "muscle gain",
    "build muscle": "muscle gain",
    "muscle gain": "muscle gain",
    "bulk": "muscle gain",
    "bulking": "muscle gain",
    "gain weight": "weight gain",
    "gaining weight": "weight gain",
    "maintain weight": "maintenance",
    "maintenance": "maintenance",
    "cut": "cutting (fat loss)",
    "cutting": "cutting (fat loss)",
    "improve fitness": "general fitness",
    "stay healthy": "general wellness",
    "eat healthy": "general wellness",
}

_DIETS = {"vegan", "vegetarian", "pescatarian", "keto", "low carb", "high protein", "gluten free", "dairy free", "halal"}


def extract_profile(text: str, profile: dict) -> dict:
    t = text.lower().strip()

    age_patterns = [
        r"\bi(?:'m| am)\s+(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|y/?o)?\b",
        r"\bage(?:d)?\s+(?:is\s+)?(\d{1,3})\b",
        r"\b(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|y\s*/\s*o)\b",
    ]
    for pat in age_patterns:
        m = re.search(pat, t)
        if m:
            age = int(m.group(1))
            if 5 <= age <= 110:
                profile["Age"] = f"{age} yrs"
                break

    m = re.search(r"(?:weigh\s+|my\s+weight\s+is\s+|weight\s+of\s+)(\d{2,3}(?:\.\d)?)\s*(kg|kgs|kilos?|lbs?|pounds?)?", t)
    if m:
        unit = (m.group(2) or "kg").lower()
        unit = unit.rstrip("s").replace("pound", "lbs").replace("kilo", "kg")
        profile["Weight"] = f"{m.group(1)} {unit}"

    m = re.search(r"(\d{1,3})\s*cm\b", t)
    if m:
        profile["Height"] = f"{m.group(1)} cm"
    else:
        m = re.search(r"(\d)\s*(?:ft|feet|')\s*(\d{1,2})\s*(?:in|inches?|\")?", t)
        if m:
            profile["Height"] = f"{m.group(1)}'{m.group(2)}\""

    m = re.search(r"blood\s*(?:type|group)\s+(?:is\s+)?([AaBbOo]{1,2}\s*[+-]?)", text)
    if m:
        profile["Blood Type"] = m.group(1).strip().upper()

    if re.search(r"\b(?:i(?:'m| am) a (?:male|man|boy|guy)|my gender is male)\b", t):
        profile["Gender"] = "Male"
    elif re.search(r"\b(?:i(?:'m| am) a? (?:female|woman|girl|lady)|my gender is female)\b", t):
        profile["Gender"] = "Female"

    existing = set(profile.get("Conditions", "").split(", ")) - {""}
    for cond in _CONDITIONS:
        if cond in t:
            existing.add(cond)
    if existing:
        profile["Conditions"] = ", ".join(sorted(existing))

    for phrase, label in _GOALS.items():
        if phrase in t:
            profile["Goal"] = label
            break

    existing_diets = set(profile.get("Diet", "").split(", ")) - {""}
    for diet in _DIETS:
        if diet in t:
            existing_diets.add(diet)
    if existing_diets:
        profile["Diet"] = ", ".join(sorted(existing_diets))

    if "allergic to" in t:
        m = re.search(r"allergic to ([a-z ,]+)", t)
        if m:
            profile["Allergies"] = m.group(1).strip()

    return profile



def build_context_string(profile: dict) -> str:
    if not profile:
        return ""
    return "User profile — " + "; ".join(f"{k}: {v}" for k, v in profile.items()) + "."



def profile_is_empty(profile: dict) -> bool:
    return not bool(profile)
