import streamlit as st
import requests
import google.generativeai as genai
import os

# Load secrets securely from Streamlit
HF_TOKEN = st.secrets["HF_TOKEN"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Tom’s Trap Tactics", layout="wide")

st.markdown("""
    <h1 style='text-align: center; font-family: monospace;'>TOM'S AI STRATEGY TERMINAL</h1>
    <p style='text-align: center; font-style: italic;'>Outsmarting Jerry — finally with intelligence</p>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💡 GEMMA Assistant", "🧠 GEMINI Assistant"])

# ------------- GEMMA Tab ----------------
with tab1:
    st.subheader("Gemma: Tactical Intelligence")

    if "gemma_messages" not in st.session_state:
        st.session_state.gemma_messages = [
            {"role": "system", "content": "You're Gemma, Tom's AI strategy assistant. Help him catch Jerry using data and wit. Be sarcastic, insightful, and helpful."}
        ]

    for msg in st.session_state.gemma_messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    gemma_input = st.chat_input("What’s your next move, Tom?", key="gemma_input")

    if gemma_input:
        st.chat_message("user").markdown(gemma_input)
        st.session_state.gemma_messages.append({"role": "user", "content": gemma_input})

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": gemma_input,
            "parameters": {"max_new_tokens": 300}
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/google/gemma-1.1-7b-it",
            headers=headers,
            json=payload
        )

        try:
            reply = response.json()[0]['generated_text']
        except:
            reply = "Gemma’s trap mechanism jammed. Try again."

        st.chat_message("assistant").markdown(reply)
        st.session_state.gemma_messages.append({"role": "assistant", "content": reply})

# ------------- GEMINI Tab ----------------
with tab2:
    st.subheader("Gemini: Creative Strategy Advisor")

    if "gemini_model" not in st.session_state:
        st.session_state.gemini_model = genai.GenerativeModel("models/gemini/gemini-1.5-flash")

    if "gemini_history" not in st.session_state:
        st.session_state.gemini_history = []

    for role, message in st.session_state.gemini_history:
        st.chat_message(role).markdown(message)

    gemini_input = st.chat_input("Alright Gemini, what's the play?", key="gemini_input")

    if gemini_input:
        st.chat_message("user").markdown(gemini_input)
        st.session_state.gemini_history.append(("user", gemini_input))

        try:
            response = st.session_state.gemini_model.generate_content(gemini_input)
            reply = response.text
        except Exception as e:
            reply = f"Gemini's circuits shorted: {e}"

        st.chat_message("assistant").markdown(reply)
        st.session_state.gemini_history.append(("assistant", reply))
