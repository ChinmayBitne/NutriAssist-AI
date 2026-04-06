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
    st.caption("Nutrition chatbot with grounded food facts")

    st.markdown("### About")
    st.write(
        "NutriAssist AI now combines local LLM responses with a nutrition dataset"
        " to answer food-related questions with more grounded facts."
    )

    st.markdown("### Dataset")
    st.write(
        "This version uses the nutrition dataset,"
        " so the chatbot can cover a broader range of meals."
    )

    st.markdown("### Performance")
    st.info(
        "On lower GPUs or CPU, model loading and replies will take more time. "
        "On stronger GPUs, the model loads faster and responses feel much smoother."
    )

    st.markdown("### Sample questions")
    st.write(
        "- How many calories are in buttermilk?\n"
        "- Is paneer good for weight loss?\n"
        "- Can I eat poha for breakfast?\n"
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
        This version adds the final combined nutrition dataset for broader and more grounded food answers.

        Try asking:
        - "How many calories are in buttermilk?"
        - "How much protein is in almonds?"
        - "Can I eat poha for breakfast?"
        - "Is paneer good for weight loss?"
        - "Can I eat chicken biryani at night?"
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
