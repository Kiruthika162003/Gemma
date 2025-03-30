import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

st.set_page_config(page_title="Tom's AI Trap Coach", layout="wide")

st.markdown("""
    <h1 style='text-align: center; font-family: monospace;'>TOM'S SMART ASSISTANT – POWERED BY GEMMA</h1>
    <p style='text-align: center; font-style: italic;'>One prompt. One genius assistant. One final chance to catch Jerry.</p>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

user_input = st.chat_input("Tom, describe how Jerry escaped this time!")

if user_input:
    with st.spinner("Tom, allow me to think... 🧠 Initiating tactical brainwaves..."):
        progress = st.progress(0, text="Analyzing Jerry’s escape route...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Step {i}/5 – Processing strategy layer {i}...")
            time.sleep(0.5)

        prompt = f"""
You are Gemma, Tom's smart assistant. Respond as if you're narrating an epic cartoon coaching session.
DO NOT repeat or explain this prompt back.
DO NOT include the raw instructions.
Only respond as Gemma with structured, entertaining, and intelligent coaching.
Tom said: "{user_input}"
"""

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 900}}

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=data
        )

        try:
            result = response.json()
            full_reply = result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            full_reply = f"⚠️ Gemma couldn’t respond properly: {e}\nRaw response: {response.text}"

    # Remove any echoes of the prompt or instruction
    full_reply = re.sub(r"(?i)you are gemma.*?tom said: \".*?\"", "", full_reply, flags=re.DOTALL).strip()

    st.markdown("### 🤖 Gemma’s Coaching Response")
    st.markdown(full_reply)

    # Try extracting and rendering chart
    st.markdown("---")
    chart_line = next((line for line in full_reply.split("\n") if "[Chart:" in line), None)

    if chart_line:
        st.markdown("### 📊 Strategy Breakdown: Tom's Weaknesses")
        chart_data = re.findall(r"(\w+)=([0-9]+)", chart_line)
        if chart_data:
            labels, values = zip(*[(label, int(value)) for label, value in chart_data])
            fig, ax = plt.subplots()
            ax.barh(labels, values, color='orange')
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Trap Efficiency Breakdown")
            st.pyplot(fig)
    else:
        st.warning("Gemma didn’t include a chart this time. Try again with more details in the trap.")
