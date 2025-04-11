import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

st.set_page_config(page_title="CAT vs RAT: Trap Mastermind", layout="wide")

st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-family:monospace; font-size: 3em;'>🎯 CAT VS RAT: TRAP MASTERMIND</h1>
        <p style='font-style: italic; font-size: 1.2em;'>Powered by Gemma — Your comically brilliant strategy assistant</p>
    </div>
    <hr style="margin-botCAT: 30px;">
""", unsafe_allow_html=True)

user_input = st.chat_input("CAT, describe how RAT escaped this time!")

if user_input:
    with st.spinner("CAT, allow me to think... 🧠 Initiating tactical brainwaves..."):
        progress = st.progress(0, text="Analyzing RAT’s escape route...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Step {i}/5 – Processing strategy layer {i}...")
            time.sleep(0.5)

        # Structured prompt (cheese strategy removed)
        prompt = f"""
You are Gemma, CAT's AI coach. Respond ONLY with a structured, witty breakdown:

1. First, guess the cartoon episode or trap style this resembles. Start with: "Episode guess: <your guess>"
2. Then provide a short funny motivational quote (use emojis).
3. Explain the failure with sarcasm and clarity.
4. Teach CAT 2-3 smart trap lessons.
5. Write a short comic-narration of RAT's escape.
6. List 3 tactical tips to improve.
7. Finally, give CAT's weaknesses in EXACT format:

[Chart: Speed=40, Stealth=55, Timing=30, Trap Quality=65]

DO NOT skip the chart. Always end with it.
CAT said: "{user_input}"
"""

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 1200}}

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

    # Clean up formatting and remove bold artifacts
    full_reply = re.sub(r"(?is)you are gemma.*?CAT said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "").strip()

    # Subtabs for clean sectioned layout
    tabs = st.tabs(["🧾 Full Response", "🎬 Episode Guess","📊 Chart"])

    with tabs[0]:
        st.markdown(full_reply)

    with tabs[1]:
        ep = re.search(r"Episode guess:(.*?)(\n|$)", full_reply, re.IGNORECASE)
        if ep:
            st.markdown(ep.group(1).strip())

    with tabs[2]:
        st.markdown("### 📊 Strategy Breakdown: CAT's Weaknesses")
        weakness_block = re.search(r"Weaknesses:(.*?)(\n\n|$)", full_reply, re.IGNORECASE | re.DOTALL)
        if weakness_block:
            chart_data = re.findall(r"(Speed|Stealth|Timing|Trap Quality)[\s:=]+(\d+)", weakness_block.group(1))
            if chart_data:
                labels, values = zip(*[(label.strip(), int(value)) for label, value in chart_data])
                fig, ax = plt.subplots()
                ax.barh(labels, values, color='skyblue')
                ax.set_xlim(0, 100)
                ax.set_xlabel("Effectiveness (%)")
                ax.set_title("Trap Efficiency Breakdown")
                st.pyplot(fig)
            else:
                st.warning("Could not extract chart values from the weaknesses section.")
        else:
            st.warning("Gemma didn't provide a weaknesses section.")
