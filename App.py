import streamlit as st
from modules.ai_router import get_response
from modules.llama_handler import warmup

st.set_page_config(
    page_title="NutriAssist AI",
    page_icon="🥗",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_ready" not in st.session_state:
    st.session_state.model_ready = False

if not st.session_state.model_ready:
    with st.spinner("Loading NutriAssist model..."):
        warmup()
    st.session_state.model_ready = True

with st.sidebar:
    st.title("🥗 NutriAssist AI")
    st.caption("Nutrition chatbot with fine-tuned response behavior")

    st.markdown("### About")
    st.write(
        "NutriAssist AI now uses a fine-tuned nutrition model so that responses are "
        "more aligned with food questions and nutrition dialogue."
    )

    st.markdown("### Fine-tuning")
    st.write(
        "This stage uses a LoRA adapter trained on nutrition-oriented prompts built "
        "from the project dataset."
    )

    st.markdown("### Performance")
    st.info(
        "On lower GPUs or CPU, model loading and replies will take more time. "
        "On stronger GPUs, the model loads faster and responses feel much smoother."
    )

    st.markdown("### Sample questions")
    st.write(
        "- Is paneer good for weight loss?\n"
        "- Can I eat poha for breakfast?\n"
        "- Suggest a healthy breakfast\n"
        "- Is chicken biryani heavy at night?"
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🥗 NutriAssist AI")
st.caption("Ask about nutrition, calories, macros, and healthy eating.")

if not st.session_state.messages:
    st.markdown(
        '''
        ### Welcome
        This version introduces a fine-tuned nutrition model for better food-oriented conversation quality.

        Try asking:
        - "Is paneer good for weight loss?"
        - "Suggest a healthy breakfast"
        - "Can I eat poha if I want a lighter meal?"
        - "Is chicken biryani heavy before sleep?"
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
