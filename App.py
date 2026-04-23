import streamlit as st
from datetime import date

from modules.ai_router import get_response
from modules.llama_handler import warmup
from modules.meal_tracker import (
    DAILY_GOALS,
    search_food,
    get_food_nutrition,
    add_meal,
    get_today_log,
    get_daily_totals,
    remove_meal,
    clear_today_log,
)

st.set_page_config(
    page_title="NutriAssist AI",
    page_icon="🥗",
    layout="wide",
)

# Session state
for key, value in {
    "messages": [],
    "model_ready": False,
    "meal_log": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Load model once
if not st.session_state.model_ready:
    with st.spinner("Loading NutriAssist model..."):
        warmup()
    st.session_state.model_ready = True

# Sidebar
with st.sidebar:
    st.title("🥗 NutriAssist AI")
    st.caption("Nutrition assistant with meal tracking")

    st.markdown("### About")
    st.write(
        "This version combines the nutrition chatbot with a meal tracker so users can "
        "ask food questions and also log meals with daily nutrition totals."
    )

    st.markdown("### Performance")
    st.info(
        "On lower GPUs or CPU, model loading and replies may take longer. "
        "On stronger GPUs, startup and generation feel much faster and smoother."
    )

    st.markdown("### What this version focuses on")
    st.write(
        "- grounded chat responses\n"
        "- daily meal logging\n"
        "- nutrition totals from the dataset"
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("Clear meal log", use_container_width=True):
        clear_today_log()
        st.rerun()

st.title("🥗 NutriAssist AI")
st.caption("Ask nutrition questions and track your meals.")

tab_chat, tab_tracker = st.tabs(["💬 Chat", "🍽️ Meal Tracker"])

# ───────── Chat ─────────
with tab_chat:
    if not st.session_state.messages:
        st.markdown(
            '''
            ### Welcome
            This version adds meal tracking while keeping the nutrition chatbot.

            Try asking:
            - "Is paneer good for weight loss?"
            - "Can I eat poha for breakfast?"
            - "How many calories are in almonds?"
            - "Suggest a healthy breakfast"
            '''
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a nutrition question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = get_response(user_input, st.session_state.messages[:-1])
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# ───────── Meal Tracker ─────────
with tab_tracker:
    st.subheader(f"Meal Tracker — {date.today()}")

    totals = get_daily_totals()
    goal_cols = st.columns(5)
    metric_defs = [
        ("Calories", "calories", "kcal"),
        ("Protein", "protein", "g"),
        ("Fat", "fat", "g"),
        ("Carbs", "carbs", "g"),
        ("Fiber", "fiber", "g"),
    ]

    for col, (label, key, unit) in zip(goal_cols, metric_defs):
        goal = DAILY_GOALS[label]
        value = totals[key]
        pct = min(int((value / goal) * 100), 100) if goal else 0
        with col:
            st.metric(label, f"{value:.1f} {unit}")
            st.progress(pct / 100 if goal else 0)

    st.markdown("---")
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown("### Add food")
        query = st.text_input("Search food", placeholder="e.g. rice, chapati, paneer")
        results = search_food(query, top_n=8) if query else None

        if results is not None and not results.empty:
            display_options = []
            option_map = {}
            for _, row in results.iterrows():
                measure = str(row.get("Measure", "")).strip()
                label = row["Food"] if not measure else f"{row['Food']} ({measure})"
                display_options.append(label)
                option_map[label] = row["Food"]

            selected_label = st.selectbox("Select match", display_options)
            selected_food = option_map[selected_label]

            fi = get_food_nutrition(selected_food)
            if fi:
                qty = st.number_input(
                    "Quantity (grams)",
                    min_value=10,
                    max_value=2000,
                    value=int(fi.get("grams", 100) or 100),
                    step=10,
                )

                scale = qty / (fi["grams"] or 100)
                preview = {
                    "Calories": round(fi["calories"] * scale, 1),
                    "Protein": round(fi["protein"] * scale, 1),
                    "Fat": round(fi["fat"] * scale, 1),
                    "Carbs": round(fi["carbs"] * scale, 1),
                    "Fiber": round(fi["fiber"] * scale, 1),
                }

                st.markdown("#### Preview")
                st.write(
                    f"**{fi['food']}** — {qty} g | "
                    f"{preview['Calories']} kcal | "
                    f"P {preview['Protein']} g | "
                    f"F {preview['Fat']} g | "
                    f"C {preview['Carbs']} g | "
                    f"Fi {preview['Fiber']} g"
                )

                if st.button("Add to log", use_container_width=True):
                    add_meal(fi, quantity_g=float(qty))
                    st.success(f"Added {fi['food']}")
                    st.rerun()
        elif query:
            st.info("No matching foods found.")

    with right:
        st.markdown("### Today's log")
        log = get_today_log()

        if not log:
            st.info("No meals added yet.")
        else:
            for i, entry in enumerate(log):
                item_cols = st.columns([4, 1.3, 0.8])
                with item_cols[0]:
                    st.markdown(
                                f"""
                            **{entry['food']}**
                            - {entry['grams']} g
                            - Protein: {entry['protein']} g
                            - Fat: {entry['fat']} g
                            - Carbs: {entry['carbs']} g
                            """
                            )
                with item_cols[1]:
                    st.write(f"**{entry['calories']} kcal**")
                with item_cols[2]:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_meal(i)
                        st.rerun()

            st.markdown("### Daily totals")
            st.json(totals)
