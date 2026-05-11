"""
App.py — NutriAssist AI
Architecture:
  - Fine-tuned Qwen/LoRA model : all chat responses
  - Gemini                     : food image detection ONLY
  - Meal Tracker               : log meals, detected foods can be added directly
"""

import re
from datetime import date

import pandas as pd
import streamlit as st
from PIL import Image

from modules import memory as mem
from modules.ai_router import get_response
from modules.gemini_handler import detect_food_from_image
from modules.llama_handler import warmup
from modules.meal_tracker import (
    DAILY_GOALS,
    add_meal,
    clear_today_log,
    get_daily_totals,
    get_food_nutrition,
    get_today_log,
    load_nutrition_db,
    remove_meal,
    search_food,
)

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="NutriAssist AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════
#  CSS — Clean Light Mode
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:wght@600;700&display=swap');

:root {
  --bg:      #f4f7f4;
  --surf:    #ffffff;
  --bdr:     #d4e2d4;
  --bdr2:    #b8d0b8;
  --acc:     #2d7a3a;
  --acc2:    #3a9e4a;
  --acc-lt:  #e6f4e8;
  --acc-dk:  #1a5225;
  --txt:     #1a2e1a;
  --txt2:    #4a6050;
  --muted:   #7a9880;
  --sh:      0 1px 4px rgba(0,40,0,0.08);
}

html,body,[class*="css"]{ font-family:'Plus Jakarta Sans',sans-serif !important; }
.stApp{ background:var(--bg) !important; color:var(--txt) !important; }
.block-container{ padding-top:1rem !important; max-width:1440px !important; }
#MainMenu,footer,header{ visibility:hidden; }

.app-hdr{
  background:linear-gradient(135deg,#fff 0%,#edf7ee 100%);
  border:1px solid var(--bdr); border-radius:16px;
  padding:18px 26px; margin-bottom:16px;
  display:flex; align-items:center; gap:18px; box-shadow:var(--sh);
}
.hdr-title{ font-family:'Lora',serif; font-size:1.7rem; color:var(--acc-dk); margin:0 0 2px; }
.hdr-sub  { color:var(--muted); font-size:0.81rem; margin:0; }
.badge    { display:inline-block; padding:2px 10px; border-radius:20px;
            font-size:0.68rem; font-weight:700; letter-spacing:0.3px; margin:5px 3px 0 0; }
.b-ll { background:#e4f5e7; color:#1a5225; border:1px solid #a8d8b0; }

.stTabs [data-baseweb="tab-list"]{
  background:var(--surf) !important; border-radius:10px !important;
  padding:4px !important; border:1px solid var(--bdr) !important;
  gap:2px !important; box-shadow:var(--sh) !important;
}
.stTabs [data-baseweb="tab"]{
  background:transparent !important; color:var(--muted) !important;
  border-radius:7px !important; font-family:'Plus Jakarta Sans',sans-serif !important;
  font-weight:600 !important; font-size:0.85rem !important;
  padding:8px 22px !important; border:none !important;
}
.stTabs [aria-selected="true"]{ background:var(--acc-lt) !important; color:var(--acc-dk) !important; }
.stTabs [data-baseweb="tab-panel"]{ padding-top:16px !important; }

.chat-wrap{
  background:var(--surf); border:1px solid var(--bdr); border-radius:14px;
  padding:18px 15px; min-height:380px; max-height:490px;
  overflow-y:auto; margin-bottom:6px; box-shadow:var(--sh);
  scrollbar-width:thin; scrollbar-color:#c8ddc8 transparent;
}
.chat-wrap::-webkit-scrollbar{ width:4px; }
.chat-wrap::-webkit-scrollbar-thumb{ background:#c8ddc8; border-radius:2px; }

.mrow{ display:flex; gap:10px; margin-bottom:13px; align-items:flex-start; animation:popIn .2s ease; }
.mrow.u{ flex-direction:row-reverse; }
@keyframes popIn{ from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:translateY(0)} }
.ava{
  width:30px; height:30px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.82rem; flex-shrink:0; margin-top:2px; box-shadow:var(--sh);
}
.ava-b{ background:var(--acc-lt); border:1px solid var(--bdr2); }
.ava-u{ background:#ddeeff; border:1px solid #a8c8f0; }
.bbl{
  max-width:68%; padding:11px 15px; border-radius:14px;
  font-size:0.87rem; line-height:1.75; white-space:pre-wrap; word-break:break-word;
}
.bbl-b{ background:#f0f9f1; border:1px solid #bcdfc4; border-top-left-radius:3px;  color:#1a3020; }
.bbl-u{ background:#eaf1fb; border:1px solid #b0cce8; border-top-right-radius:3px; color:#1a2e50; }

.welcome{ text-align:center; padding:48px 16px; }
.welcome .wico{ font-size:3.2rem; margin-bottom:10px; }
.welcome h3{ font-family:'Lora',serif; font-size:1.3rem; color:var(--acc-dk); margin-bottom:8px; }
.welcome p{ font-size:0.85rem; line-height:1.9; color:#5a7860; }
.hints{ display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:16px; }
.hint{ background:var(--acc-lt); border:1px solid var(--bdr2); border-radius:20px;
       padding:5px 13px; font-size:0.76rem; color:var(--acc-dk); }

[data-testid="stSidebar"]{ background:#f6faf6 !important; border-right:1px solid var(--bdr) !important; }
[data-testid="stSidebar"] > div{ padding:0.9rem 0.8rem !important; }

.card{ background:var(--surf); border:1px solid var(--bdr); border-radius:12px;
       padding:13px 15px; margin-bottom:13px; box-shadow:var(--sh); }
.ctitle{ font-size:0.66rem; font-weight:700; text-transform:uppercase;
         letter-spacing:1.4px; color:var(--acc); margin-bottom:9px; }
.ptag{ display:inline-block; background:var(--acc-lt); border:1px solid var(--bdr2);
       border-radius:6px; padding:2px 9px; font-size:0.73rem; color:var(--acc-dk); margin:2px; }
.pempty{ color:#9ab8a0; font-size:0.78rem; font-style:italic; line-height:1.7; }

.food-chip-row{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0; }
.food-chip{
  background:#fff8ec; border:1px solid #f0c060;
  border-radius:20px; padding:5px 14px;
  font-size:0.78rem; color:#7a4e00; font-weight:500;
  display:inline-flex; align-items:center; gap:5px;
}

.mrow2{ display:flex; justify-content:space-between; align-items:center;
        margin-bottom:3px; font-size:0.78rem; }
.mlbl{ color:var(--txt2); font-weight:500; }
.mval{ color:var(--acc); font-weight:700; font-size:0.73rem; }
.bar-bg{ background:#deeede; border-radius:3px; height:5px; margin-bottom:8px; overflow:hidden; }
.bar-fg{ height:5px; border-radius:3px; }

.mbox{ background:var(--surf); border:1px solid var(--bdr); border-radius:12px;
       padding:15px 10px; text-align:center; box-shadow:var(--sh); }
.mv  { font-size:1.5rem; font-weight:700; margin-bottom:2px; }
.ml  { font-size:0.64rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.8px; }
.mbg { background:#deeede; border-radius:3px; height:4px; margin-top:8px; overflow:hidden; }
.mfg { height:4px; border-radius:3px; }
.mpct{ font-size:0.62rem; color:var(--muted); text-align:right; margin-top:2px; }

.meal-r{ background:var(--surf); border:1px solid var(--bdr); border-radius:10px;
         padding:9px 13px; margin-bottom:7px; box-shadow:var(--sh); }
.meal-n{ font-size:0.86rem; color:var(--txt); font-weight:600; }
.meal-s{ font-size:0.71rem; color:var(--muted); margin-top:2px; }

.stTextInput>div>div>input,
.stNumberInput>div>div>input{
  background:var(--surf) !important; border:1px solid var(--bdr) !important;
  border-radius:8px !important; color:var(--txt) !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{
  border-color:var(--acc2) !important;
  box-shadow:0 0 0 2px rgba(45,122,58,.12) !important;
}
.stSelectbox [data-baseweb="select"]>div{
  background:var(--surf) !important; border-color:var(--bdr) !important; color:var(--txt) !important;
}
.stChatInput>div{
  background:var(--surf) !important; border:1px solid var(--bdr2) !important;
  border-radius:12px !important; box-shadow:var(--sh) !important;
}
.stChatInput input{ color:var(--txt) !important; font-family:'Plus Jakarta Sans',sans-serif !important; }

.stButton>button{
  background:var(--acc-lt) !important; border:1px solid var(--bdr2) !important;
  color:var(--acc-dk) !important; border-radius:8px !important;
  font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:600 !important;
  font-size:0.81rem !important; transition:all .15s !important;
}
.stButton>button:hover{
  background:var(--acc) !important; border-color:var(--acc-dk) !important;
  color:#fff !important; box-shadow:var(--sh) !important;
}

hr{ border-color:var(--bdr) !important; }
.stSuccess{ background:var(--acc-lt) !important; border-color:var(--bdr2) !important; color:var(--acc-dk) !important; }
.stInfo   { background:#eef2ff !important; border-color:#9ab0f0 !important; color:#1a3070 !important; }
.stDataFrame{ border:1px solid var(--bdr) !important; border-radius:10px !important; overflow:hidden !important; }
.stSpinner>div{ border-color:var(--acc) !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
for _k, _v in {
    "messages": [],
    "user_profile": {},
    "detected_foods": [],
    "last_img_id": None,
    "meal_log": {},
    "model_ready": False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def _e(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_chat():
    if not st.session_state.messages:
        st.markdown(
            """
        <div class="welcome">
          <div class="wico">🥗</div>
          <h3>Welcome to NutriAssist AI</h3>
          <p>
            Ask me anything about nutrition, healthy eating, or diet planning.<br>
            Tell me your age, weight, or health conditions for personalised advice.<br>
            Upload a meal photo — I'll detect the food and let you log it directly.
          </p>
          <div class="hints">
            <span class="hint">💬 What should I eat to gain weight?</span>
            <span class="hint">🥩 I'm 23, 62 kg — best protein sources?</span>
            <span class="hint">📋 Make me a 2500 kcal meal plan</span>
            <span class="hint">🩺 I have diabetes — what to avoid?</span>
          </div>
        </div>""",
            unsafe_allow_html=True,
        )
        return

    parts = ['<div class="chat-wrap" id="cw">']
    for m in st.session_state.messages:
        u = m["role"] == "user"
        rc = "mrow u" if u else "mrow"
        ac = "ava-u" if u else "ava-b"
        bc = "bbl bbl-u" if u else "bbl bbl-b"
        em = "🧑" if u else "🥗"
        parts.append(
            '<div class="{}"><div class="ava {}">{}</div>'
            '<div class="{}">{}</div></div>'.format(rc, ac, em, bc, _e(m["content"]))
        )
    parts.append("</div>")
    parts.append("<script>(function(){var e=document.getElementById('cw');if(e)e.scrollTop=e.scrollHeight;})();</script>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_profile():
    p = st.session_state.user_profile
    st.markdown('<div class="card"><div class="ctitle">👤 Your Profile</div>', unsafe_allow_html=True)
    if p:
        st.markdown("".join('<span class="ptag">{}: {}</span>'.format(k, v) for k, v in p.items()), unsafe_allow_html=True)
    else:
        st.markdown('<p class="pempty">Tell me your age, weight,<br>or health conditions!</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if p and st.button("🗑 Clear Profile", use_container_width=True, key="clr_p"):
        st.session_state.user_profile = {}
        st.rerun()


def render_macro_mini():
    t = get_daily_totals()
    if not get_today_log():
        return
    st.markdown('<div class="ctitle">📊 Today\'s Progress</div>', unsafe_allow_html=True)
    for label, key, color, unit in [
        ("Calories", "calories", "#f59e0b", "kcal"),
        ("Protein", "protein", "#3b82f6", "g"),
        ("Fat", "fat", "#ef4444", "g"),
        ("Carbs", "carbs", "#a855f7", "g"),
    ]:
        goal = DAILY_GOALS[label]
        val = t[key]
        pct = min(int(val / goal * 100), 100) if goal else 0
        st.markdown(
            '<div class="mrow2"><span class="mlbl">{}</span>'
            '<span class="mval">{:.0f}/{} {}</span></div>'
            '<div class="bar-bg"><div class="bar-fg" style="width:{}%;background:{}"></div></div>'.format(
                label, val, goal, unit, pct, color
            ),
            unsafe_allow_html=True,
        )


def _safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _normalize_measure(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _infer_quantity_mode(food_info: dict) -> str:
    explicit_mode = str(food_info.get("quantity_mode", "")).lower().strip()
    if explicit_mode in {"count", "grams"}:
        return explicit_mode

    measure = _normalize_measure(food_info.get("measure", ""))
    food = _normalize_measure(food_info.get("food", ""))

    count_tokens = [
        "piece", "pieces", "pc", "pcs", "count", "chapati", "roti", "phulka",
        "idli", "dosa", "egg", "eggs", "cup", "cups", "slice", "slices",
        "bowl", "bowls", "glass", "glasses", "serving", "servings",
    ]
    gram_tokens = ["g", "gram", "grams", "100g", "per 100g"]

    if any(tok in measure for tok in count_tokens):
        return "count"
    if any(tok in measure for tok in gram_tokens):
        return "grams"

    if any(tok in food for tok in ["chapati", "roti", "idli", "dosa", "egg", "banana", "apple", "orange"]):
        return "count"

    grams = _safe_float(food_info.get("grams", 0.0), 0.0)
    if grams and grams <= 80 and measure:
        return "count"
    return "grams"


def _suggest_quantity(food_info: dict):
    mode = _infer_quantity_mode(food_info)
    measure = str(food_info.get("measure", "")).strip()
    grams = _safe_float(food_info.get("grams", 0.0), 0.0)

    if mode == "count":
        default_count = 1.0
        if any(tok in _normalize_measure(measure) for tok in ["cup", "bowl", "glass"]):
            default_count = 1.0
        elif any(tok in _normalize_measure(measure) for tok in ["slice", "piece", "chapati", "roti", "idli", "egg"]):
            default_count = 1.0
        return mode, int(default_count), measure or "1 serving"

    default_grams = int(round(grams)) if grams and grams >= 5 else 100
    if default_grams < 5:
        default_grams = 100
    return mode, default_grams, measure or f"{default_grams} g"


def _calc_scale(food_info: dict, quantity_value: float, quantity_mode: str) -> float:
    if quantity_mode == "count":
        return max(float(quantity_value), 0.0)
    base_grams = _safe_float(food_info.get("grams", 0.0), 100.0) or 100.0
    return max(float(quantity_value), 0.0) / base_grams


def _smart_add_detected_food(food_name: str):
    fi = get_food_nutrition(food_name)
    if not fi:
        st.warning("Not found in DB")
        return

    mode, suggestion, _ = _suggest_quantity(fi)
    if mode == "count":
        entry = add_meal(fi, quantity_count=float(suggestion))
        st.success(f"Added {entry['food']} ({int(suggestion)} count)")
    else:
        entry = add_meal(fi, quantity_g=float(suggestion))
        st.success(f"Added {entry['food']} ({int(suggestion)} g)")


def _meal_qty_text(entry: dict) -> str:
    quantity = entry.get("quantity")
    unit = str(entry.get("quantity_unit", "")).strip()
    measure = str(entry.get("measure", "")).strip()
    grams = entry.get("grams")

    if quantity is not None and unit:
        q = int(quantity) if float(quantity).is_integer() else round(float(quantity), 1)
        if unit == "count":
            if measure:
                return f"{q} × {measure}"
            return f"{q} count"
        if unit == "grams":
            return f"{int(round(float(quantity)))} g"

    if grams is not None:
        try:
            return f"{int(round(float(grams)))} g"
        except Exception:
            pass
    return measure or "1 serving"


# Warm model once per app process
if not st.session_state.model_ready:
    with st.spinner("Initializing nutrition model..."):
        warmup()
    st.session_state.model_ready = True

# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
        '<span style="font-size:1.9rem">🥗</span>'
        '<div><div style="font-family:\'Lora\',serif;color:#1a5225;font-size:1.1rem;font-weight:700">NutriAssist</div>'
        '<div style="color:#7a9880;font-size:0.7rem">AI Nutrition Advisor</div></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    render_profile()
    st.divider()
    render_macro_mini()
    st.divider()

    st.markdown('<div class="ctitle">📸 Food Image Analysis</div>', unsafe_allow_html=True)
    st.caption("Upload a meal photo — I'll detect the food items for you.")

    uploaded = st.file_uploader(
        "Upload meal image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="img_up",
    )

    if uploaded is not None:
        if uploaded.file_id != st.session_state.last_img_id:
            st.session_state.last_img_id = uploaded.file_id
            st.session_state.detected_foods = []
            img = Image.open(uploaded)
            st.image(img, caption="Uploaded image")
            with st.spinner("🔍 Detecting food items…"):
                foods = detect_food_from_image(img)
            st.session_state.detected_foods = foods
        else:
            st.image(Image.open(uploaded))

    if st.session_state.detected_foods:
        st.markdown('<div class="ctitle" style="margin-top:10px">🍽️ Detected Foods</div>', unsafe_allow_html=True)
        for food in st.session_state.detected_foods:
            fi = get_food_nutrition(food)
            mode, suggestion, label = _suggest_quantity(fi) if fi else ("grams", 100, "100 g")
            col_name, col_hint, col_btn = st.columns([2.4, 1.2, 0.8])
            with col_name:
                st.markdown('<span class="food-chip">🍴 {}</span>'.format(_e(food)), unsafe_allow_html=True)
            with col_hint:
                st.caption(f"Add: {label if mode == 'count' else str(suggestion) + ' g'}")
            with col_btn:
                if st.button("➕", key=f"add_img_{food}", help="Add to tracker"):
                    _smart_add_detected_food(food)
                    st.rerun()

        food_list = ", ".join(st.session_state.detected_foods)
        if st.button("💬 Ask about this meal", use_container_width=True, key="ask_img"):
            question = f"I'm eating {food_list}. Is this a good choice for my health? What are the nutritional highlights?"
            st.session_state.user_profile = mem.extract_profile(question, st.session_state.user_profile)
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking…"):
                resp = get_response(question, st.session_state.messages[:-1], st.session_state.user_profile, detected_foods=st.session_state.detected_foods)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.button("🍽 Clear Log", use_container_width=True):
            clear_today_log()
            st.rerun()
    st.divider()
    st.caption(
        "💡 **Tips**\n"
        "- Share age & weight for personalised advice\n"
        "- Mention conditions (diabetes, hypertension…)\n"
        "- Upload a photo → detect food → add to tracker"
    )

# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════
st.markdown(
    """
<div class="app-hdr">
  <span style="font-size:2.8rem;line-height:1">🥗</span>
  <div>
    <div class="hdr-title">NutriAssist AI</div>
    <p class="hdr-sub">Your personalised nutrition advisor — powered by a fine-tuned model</p>
    <span class="badge b-ll">🤖 Fine-tuned Nutrition Model</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

tab_chat, tab_tracker, tab_db = st.tabs(["💬  Chat", "🍽️  Meal Tracker", "🔍  Food Database"])

# ──────────────────────────────────────────────
#  TAB 1 — CHAT
# ──────────────────────────────────────────────
with tab_chat:
    render_chat()

    user_input = st.chat_input("Ask about nutrition, your diet, or any food…")

    if user_input:
        st.session_state.user_profile = mem.extract_profile(user_input, st.session_state.user_profile)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking…"):
            resp = get_response(
                user_input,
                history=st.session_state.messages[:-1],
                profile=st.session_state.user_profile,
                detected_foods=st.session_state.detected_foods,
            )
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.rerun()

# ──────────────────────────────────────────────
#  TAB 2 — MEAL TRACKER
# ──────────────────────────────────────────────
with tab_tracker:
    st.markdown(
        "### 🍽️ Meal Tracker "
        "<span style='font-size:0.77rem;color:#7a9880;font-weight:400'>"
        f"— {date.today().strftime('%A, %B %d %Y')}</span>",
        unsafe_allow_html=True,
    )

    totals = get_daily_totals()
    defs = [
        ("Calories", "calories", "kcal", "#f59e0b"),
        ("Protein", "protein", "g", "#3b82f6"),
        ("Fat", "fat", "g", "#ef4444"),
        ("Carbs", "carbs", "g", "#a855f7"),
        ("Fiber", "fiber", "g", "#22c55e"),
    ]
    for col, (label, key, unit, color) in zip(st.columns(5), defs):
        goal = DAILY_GOALS[label]
        val = totals[key]
        pct = min(int(val / goal * 100), 100) if goal else 0
        with col:
            st.markdown(
                '<div class="mbox">'
                '<div class="mv" style="color:{}">{:.0f}</div>'
                '<div class="ml">{} ({})</div>'
                '<div class="mbg"><div class="mfg" style="width:{}%;background:{}"></div></div>'
                '<div class="mpct">{}% of {}</div>'
                '</div>'.format(color, val, label, unit, pct, color, pct, goal),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_add, col_log = st.columns([1, 1], gap="large")

    with col_add:
        st.markdown("#### ➕ Log a Meal")
        fq = st.text_input("Search food", placeholder="e.g. chicken breast, chapati, oats…", key="fq")

        sr = pd.DataFrame()
        sel = None
        fi_preview = None
        qty_mode = "grams"
        qty = None
        suggestion_label = ""

        if fq and len(fq.strip()) >= 2:
            sr = search_food(fq.strip(), top_n=8)

        if not sr.empty:
            option_labels = []
            option_map = {}
            for _, row in sr.iterrows():
                label = row["Food"]
                measure = str(row.get("Measure", "")).strip() if "Measure" in sr.columns else ""
                if measure:
                    label = f"{label} ({measure})"
                option_labels.append(label)
                option_map[label] = row["Food"]

            sel_label = st.selectbox("Select best match", option_labels, key="fsel")
            sel = option_map.get(sel_label)
            fi_preview = get_food_nutrition(sel)

            if fi_preview:
                qty_mode, qty_default, suggestion_label = _suggest_quantity(fi_preview)
                if qty_mode == "count":
                    qty = st.number_input(
                        "Quantity (count)",
                        min_value=1,
                        max_value=20,
                        value=int(qty_default),
                        step=1,
                        key="qty_count",
                    )
                else:
                    qty = st.number_input(
                        "Quantity (grams)",
                        min_value=5,
                        max_value=2000,
                        value=int(qty_default),
                        step=5,
                        key="qty_g",
                    )
                st.caption(f"Suggested portion: {suggestion_label}")

                sc = _calc_scale(fi_preview, qty, qty_mode)
                st.markdown(
                    '<div style="background:#f0f9f1;border:1px solid #b8d8bc;border-radius:8px;'
                    'padding:8px 12px;font-size:0.76rem;color:#2a5430;margin:6px 0">'
                    '<b>{}</b> — {} &nbsp;'
                    '🔥 {:.0f} kcal &nbsp;'
                    '🥩 {:.1f}g protein &nbsp;'
                    '🧈 {:.1f}g fat &nbsp;'
                    '🌾 {:.1f}g carbs</div>'.format(
                        _e(fi_preview.get("food", sel)),
                        _e(_meal_qty_text({
                            "quantity": qty,
                            "quantity_unit": qty_mode,
                            "measure": fi_preview.get("measure", ""),
                            "grams": qty if qty_mode == "grams" else fi_preview.get("grams", ""),
                        })),
                        _safe_float(fi_preview.get("calories", 0)) * sc,
                        _safe_float(fi_preview.get("protein", 0)) * sc,
                        _safe_float(fi_preview.get("fat", 0)) * sc,
                        _safe_float(fi_preview.get("carbs", 0)) * sc,
                    ),
                    unsafe_allow_html=True,
                )

            if st.button("➕ Add to Log", use_container_width=True, key="add_btn"):
                fi = get_food_nutrition(sel)
                if fi:
                    if qty_mode == "count":
                        e = add_meal(fi, quantity_count=float(qty))
                    else:
                        e = add_meal(fi, quantity_g=float(qty))
                    st.success(f"✅ Logged: {e['food']} — {e['calories']} kcal")
                    st.rerun()
        elif fq and len(fq.strip()) >= 2:
            st.caption("⚠️ No match found. Try a different term.")

    with col_log:
        st.markdown("#### 📋 Today's Log")
        log = get_today_log()
        if not log:
            st.markdown('<p class="pempty" style="padding:20px 0">No meals logged yet.<br>Search a food on the left!</p>', unsafe_allow_html=True)
        else:
            for i, entry in enumerate(log):
                c1, c2, c3 = st.columns([4, 1.5, 0.5])
                with c1:
                    st.markdown(
                        '<div class="meal-r"><div class="meal-n">{}</div>'
                        '<div class="meal-s">{} · P {}g · F {}g · C {}g</div></div>'.format(
                            _e(entry.get("food", "")),
                            _e(_meal_qty_text(entry)),
                            entry.get("protein", 0),
                            entry.get("fat", 0),
                            entry.get("carbs", 0),
                        ),
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        '<div style="padding-top:13px;font-size:0.84rem;color:#2d7a3a;'
                        'font-weight:700;text-align:right">{} kcal</div>'.format(entry.get("calories", 0)),
                        unsafe_allow_html=True,
                    )
                with c3:
                    if st.button("✕", key=f"d{i}", help="Remove"):
                        remove_meal(i)
                        st.rerun()

            st.markdown(
                '<div style="text-align:right;font-size:0.76rem;color:#7a9880;margin-top:3px">'
                'Total: <b style="color:#2d7a3a">{:.0f} kcal</b></div>'.format(totals["calories"]),
                unsafe_allow_html=True,
            )

# ──────────────────────────────────────────────
#  TAB 3 — FOOD DATABASE
# ──────────────────────────────────────────────
with tab_db:
    st.markdown("### 🔍 Food Nutrition Database")
    db = load_nutrition_db()
    if db.empty:
        st.warning("⚠️ Copy your nutrients.csv into the data/ folder and restart.")
    else:
        st.caption(f"Searchable database of {len(db)} food items.")
        dbq = st.text_input("Search food", placeholder="e.g. egg, salmon, avocado…", key="dbq")
        dcols = [c for c in ["Food", "Measure", "Grams", "Calories", "Protein", "Fat", "Sat.Fat", "Fiber", "Carbs"] if c in db.columns]

        if dbq and len(dbq.strip()) >= 2:
            res = search_food(dbq.strip(), top_n=20)
            if not res.empty:
                st.caption(f"{len(res)} result(s) found")
                st.dataframe(res[dcols].reset_index(drop=True), width="stretch", hide_index=True)
                st.markdown("**Quick-add to today's log:**")
                qa1, qa2, qa3 = st.columns([3, 1.5, 1])
                option_labels = []
                option_map = {}
                for _, row in res.iterrows():
                    label = row["Food"]
                    measure = str(row.get("Measure", "")).strip() if "Measure" in res.columns else ""
                    if measure:
                        label = f"{label} ({measure})"
                    option_labels.append(label)
                    option_map[label] = row["Food"]
                with qa1:
                    qaf_label = st.selectbox("Food", option_labels, key="qaf", label_visibility="collapsed")
                    qaf = option_map[qaf_label]
                qfi = get_food_nutrition(qaf)
                qmode, qdefault, qlabel = _suggest_quantity(qfi) if qfi else ("grams", 100, "100 g")
                with qa2:
                    if qmode == "count":
                        qaq = st.number_input("count", min_value=1, max_value=20, value=int(qdefault), step=1, key="qaq_count", label_visibility="collapsed")
                    else:
                        qaq = st.number_input("g", min_value=5, max_value=2000, value=int(qdefault), step=5, key="qaq_g", label_visibility="collapsed")
                with qa3:
                    if st.button("➕ Add", key="qa_add", use_container_width=True):
                        fi = get_food_nutrition(qaf)
                        if fi:
                            if qmode == "count":
                                e = add_meal(fi, quantity_count=float(qaq))
                            else:
                                e = add_meal(fi, quantity_g=float(qaq))
                            st.success(f"Added {e['food']} — {e['calories']} kcal")
                            st.rerun()
                st.caption(f"Suggested portion: {qlabel}")
            else:
                st.info("No results found. Try a different search term.")
        else:
            st.caption("Showing first 25 foods. Type above to search.")
            st.dataframe(db[dcols].head(25).reset_index(drop=True), width="stretch", hide_index=True)
