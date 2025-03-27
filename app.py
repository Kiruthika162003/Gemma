import streamlit as st
from gemma import gm

# Load Gemma model and parameters (Gemma 3 - 4B Instruct)
@st.cache_resource(show_spinner="Loading Gemma 3 model...")
def load_model():
    model = gm.nn.Gemma3_4B()
    params = gm.ckpts.load_params(gm.ckpts.CheckpointPath.GEMMA3_4B_IT)
    return gm.text.ChatSampler(model=model, params=params, multi_turn=True)

sampler = load_model()

# Streamlit UI Setup
st.set_page_config(page_title="Tom’s AI Assistant", layout="centered")
st.title("🐱 Tom’s AI Strategy Assistant (Powered by Gemma 3)")

st.markdown(
    "Ask any question about trap strategy, past episode failures, or anything else. "
    "Gemma will analyze and respond like a master strategist."
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input prompt
user_prompt = st.text_input("🧠 Your prompt:", placeholder="Why did my trap fail in 'The Mouse Trap'?")

if st.button("Ask Gemma") and user_prompt:
    st.session_state.chat_history.append(("You", user_prompt))
    with st.spinner("Gemma is thinking..."):
        try:
            response = sampler.chat(user_prompt)
        except Exception as e:
            response = f"⚠️ Error: {e}"
    st.session_state.chat_history.append(("Gemma", response))

# Display chat history
for speaker, msg in reversed(st.session_state.chat_history):
    st.markdown(f"**{speaker}:** {msg}")
