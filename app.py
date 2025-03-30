import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]

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

        prompt = f""" please donot print this prompt.
Act as Gemma, Tom's smart assistant. You are sarcastic, funny, emotionally supportive, and extremely strategic. Respond in a structured and entertaining format:

1. Start with a funny motivational message to Tom with emojis.
2. Guess which cartoon episode or trap style this resembles.
3. Analyze why the plan failed in a witty, smart way.
4. Teach Tom 2-3 solid lessons to improve.
5. Describe the escape in a comic-book style (use metaphors and fun tone).
6. Suggest tactical enhancements.
7. Give a breakdown chart of Tom's current weaknesses like:

   [Chart: Speed=40, Stealth=55, Timing=30, Trap Quality=65, Cheese Placement=50]

Make it long, dramatic, and entertaining like a narrator coaching a struggling cartoon hero.

Situation: "{user_input}"
"""

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 900}}

        response = requests.post("https://api-inference.huggingface.co/models/google/gemma-7b-it",
,
            headers=headers,
            json=data
        )

        try:
            result = response.json()
            full_reply = result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            full_reply = f"⚠️ Gemma couldn’t respond properly: {e}"

    # Show final result
    st.markdown("### 🤖 Gemma’s Coaching Response")
    st.markdown(full_reply)

    # Try extracting and rendering chart
    st.markdown("---")
    chart_line = next((line for line in full_reply.split("\n") if "[Chart:" in line), None)

    if chart_line:
        st.markdown("### 📊 Strategy Breakdown: Tom's Weaknesses")
        chart_data = re.findall(r"(\\w+)=([0-9]+)", chart_line)
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
