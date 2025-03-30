import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re

# Load Hugging Face Token securely from Streamlit secrets
HF_TOKEN = st.secrets["HF_TOKEN"]

st.set_page_config(page_title="Tom's AI Trap Coach", layout="wide")

st.markdown("""
    <h1 style='text-align: center; font-family: monospace;'>TOM'S SMART ASSISTANT – POWERED BY GEMMA</h1>
    <p style='text-align: center; font-style: italic;'>One prompt. One genius assistant. One final chance to catch Jerry.</p>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

# Single prompt from user (Tom)
user_input = st.chat_input("Tom, describe how Jerry escaped this time!")

if user_input:
    # GEMMA structured prompt
    prompt = f"""
You are Gemma, Tom's smart assistant. Respond with a long, structured, witty response:

1. Motivate Tom (use emojis).
2. Identify what episode/trap this feels like.
3. Explain why the plan failed.
4. Teach 2-3 lessons to improve next time.
5. Create a funny comic-style narrative.
6. Suggest tactical improvements.
7. Finally, include a chart of Tom's current weaknesses like:

   [Chart: Speed=40, Stealth=55, Timing=30, Trap Quality=65, Cheese Placement=50]

Tom said: "{user_input}"
"""

    # Call Hugging Face Inference API (Gemma)
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": prompt, "parameters": {"max_new_tokens": 900}}

    response = requests.post(
        "https://api-inference.huggingface.co/models/google/gemma-1.1-7b-it",
        headers=headers,
        json=data
    )

    try:
        result = response.json()
        full_reply = result[0]['generated_text'] if isinstance(result, list) else str(result)
    except Exception as e:
        full_reply = f"⚠️ Error from Gemma: {e}"

    # Show Gemma's full response
    st.markdown("### 🤖 Gemma’s Full Response")
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
            ax.barh(labels, values)
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Trap Efficiency Factors")
            st.pyplot(fig)
    else:
        st.warning("Gemma didn’t return chart data this time. Try a more detailed prompt.")
