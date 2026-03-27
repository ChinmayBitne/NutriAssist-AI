import streamlit as st

from modules.ai_router import get_response
from modules.llama_handler import warmup

# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="NutriAssist AI",
    page_icon="🥗",
    layout="wide",
)

# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_ready" not in st.session_state:
    st.session_state.model_ready = False

# ------------------------------------------------------------
# Warm up model once per app session
# ------------------------------------------------------------
if not st.session_state.model_ready:
    with st.spinner("Loading NutriAssist model..."):
        warmup()
    st.session_state.model_ready = True

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
with st.sidebar:
    st.title("🥗 NutriAssist AI")
    st.caption("AI-powered nutrition chatbot")

    st.markdown("### About")
    st.write(
        "NutriAssist AI is a simple nutrition chatbot that answers general "
        "questions about food, healthy eating, calories, and diet basics."
    )

    st.markdown("### What this version focuses on")
    st.write(
        "- Local LLM-based chat\n"
        "- Simple conversational interface\n"
        "- General nutrition guidance"
    )

    st.markdown("### Performance")
    st.info(
        "On lower GPUs or CPU, model loading and responses may take longer. "
        "On stronger GPUs, the chatbot becomes much faster and smoother."
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------
# Main header
# ------------------------------------------------------------
st.title("🥗 NutriAssist AI")
st.caption("Ask simple questions about food, calories, and healthy eating.")

# ------------------------------------------------------------
# Welcome / empty state
# ------------------------------------------------------------
if not st.session_state.messages:
    st.info("Ask anything about food, nutrition, calories, or healthy eating.")

    st.markdown(
        """
        ### Try asking:
        - Is paneer good for weight loss?
        - Suggest a healthy breakfast
        - How much protein is in eggs?
        - What should I eat after workout?
        """
    )

# ------------------------------------------------------------
# Render previous chat messages
# ------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------------------------------------------------
# Chat input
# ------------------------------------------------------------
user_input = st.chat_input("Ask about food, calories, or healthy eating...")

if user_input:
    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_response(user_input, st.session_state.messages[:-1])
        st.markdown(reply)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})