import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-2b-it"

st.set_page_config(page_title="Prince vs Dragon: Rescue Mastermind", layout="wide")

st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-family:monospace; font-size: 3em;'>👑 PRINCE VS DRAGON: RESCUE MASTERMIND</h1>
        <p style='font-style: italic; font-size: 1.2em;'>Powered by Gemma 3 — Your heroic AI strategy assistant</p>
    </div>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

st.markdown("""
> 🐉 The prince has tried for decades — swords, spells, catapults… always eaten.  
> But what if **AI** could finally help him rescue the princess from Dragon?  
> No more charging blindly. No more failure.  
> **Meet Prince AI Strategy Assistant** — built with Google’s **Gemma 3**.
""")

user_input = st.chat_input("PRINCE, describe how the DRAGON foiled your rescue attempt this time!")

if user_input:
    with st.spinner("PRINCE, allow me to consult the scrolls of strategy... 🧠 Loading royal tactics..."):
        progress = st.progress(0, text="Analyzing DRAGON's counter-strategy...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Step {i}/5 – Processing wisdom layer {i}...")
            time.sleep(0.5)
            prompt = f"""
You are Gemma, PRINCE's AI strategy advisor. Your job is to respond with a professional and structured rescue review using the following format. Do not include jokes or comical content.

Structure your response with these labeled sections:

[What prince tried]
Explain once again.

[What Went Well]
List 5 specific strengths or aspects of the prince’s plan that were well-conceived or executed.

[What Didn't Work]
List 5 specific points where the plan failed due to execution gaps, external interference, or planning errors.

[Improved Strategy Plan]
List 5 well-thought-out, realistic suggestions the prince can follow to succeed next time. Be clear and concise.

[Rescue Metrics]
Format exactly like this:
[Chart: Courage=70, Timing=45, Magic Usage=30, Rescue Planning=55]

PRINCE said: "{user_input}"
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

    # Clean up formatting and remove prompt artifacts
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "").strip()

    # Subtabs for clean display
    tabs = st.tabs(["🧾 Full Response", "📊  Stats"])

    with tabs[0]:
        st.markdown(full_reply)


    with tabs[1]:
        st.markdown("### 📊 Heroic Breakdown: PRINCE’s Weaknesses")
        weakness_block = re.search(r"Chart:(.*?)(\n\n|$)", full_reply, re.IGNORECASE | re.DOTALL)
        if weakness_block:
            chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", weakness_block.group(1))
            if chart_data:
                labels, values = zip(*[(label.strip(), int(value)) for label, value in chart_data])
                fig, ax = plt.subplots()
                ax.barh(labels, values)
                ax.set_xlim(0, 100)
                ax.set_xlabel("Effectiveness (%)")
                ax.set_title("Rescue Strategy Breakdown")
                st.pyplot(fig)
            else:
                st.warning("Could not extract values for the chart.")
        else:
            st.warning("Gemma didn't include a chart this time.")
