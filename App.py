import streamlit as st
from modules.ai_router import get_response
from modules.llama_handler import warmup

st.set_page_config(page_title="NutriAssist AI - v1", page_icon="🥗", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_ready" not in st.session_state:
    st.session_state.model_ready = False

if not st.session_state.model_ready:
    with st.spinner("Loading model..."):
        warmup()
    st.session_state.model_ready = True

st.title("🥗 NutriAssist AI")
st.caption("v1 — Basic chatbot")

with st.sidebar:
    st.subheader("About v1")
    st.write("This version is a simple nutrition chatbot using a local LLM.")
    st.write("No nutrition dataset, no meal tracker, no memory, no image analysis.")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

chat_box = st.container()

with chat_box:
    if not st.session_state.messages:
        st.info("Ask anything about food, nutrition, calories, or healthy eating.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
