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
            "model": "google/gemma-2b-it",
            "messages": st.session_state.gemma_messages,
            "temperature": 0.8,
            "max_tokens": 512
        }

        response = requests.post(
            "https://api-inference.huggingface.co/v1/chat/completions",
            headers=headers,
            json=payload
        )

        try:
            reply = response.json()["choices"][0]["message"]["content"]
        except:
            reply = "Gemma’s trap mechanism jammed. Try again."

        st.chat_message("assistant").markdown(reply)
        st.session_state.gemma_messages.append({"role": "assistant", "content": reply})

# ------------- GEMINI Tab ----------------
with tab2:
    st.subheader("Gemini: Creative Strategy Advisor")

    if "gemini_chat" not in st.session_state:
        genai_model = genai.GenerativeModel("gemini-pro")
        st.session_state.gemini_chat = genai_model.start_chat(history=[
            {"role": "user", "parts": ["You're Gemini, Tom's creative, chaotic assistant. Help him outwit Jerry with wild ideas, humor, and innovation."]},
        ])

    for message in st.session_state.gemini_chat.history:
        role = "user" if message.role == "user" else "assistant"
        parts = message.parts

        # Convert all parts to string safely
        if isinstance(parts, list):
            content = " ".join([p if isinstance(p, str) else str(p) for p in parts])
        else:
            content = str(parts)

        st.chat_message(role).markdown(content)

    gemini_input = st.chat_input("Alright Gemini, what's the play?", key="gemini_input")

    if gemini_input:
        st.chat_message("user").markdown(gemini_input)
        response = st.session_state.gemini_chat.send_message(gemini_input)
        st.chat_message("assistant").markdown(response.text)
