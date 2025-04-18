import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Gemini API Token securely
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
gemini_endpoint = "https://api.gemini.com/v1/strategy"  # Replace with the correct Gemini API endpoint

st.set_page_config(page_title="Prince vs Dragon: Rescue Mastermind", layout="wide")

st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-family:monospace; font-size: 3em;'>👑 PRINCE VS DRAGON: RESCUE MASTERMIND</h1>
        <p style='font-style: italic; font-size: 1.2em;'>Powered by Gemini — Your heroic AI strategy assistant</p>
    </div>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

st.markdown("""
> 🐉 The prince has tried for decades — swords, spells, catapults… always eaten.  
> But what if **AI** could finally help him rescue the princess from Dragon?  
> No more charging blindly. No more failure.  
> **Meet Prince AI Strategy Assistant** — built with **Gemini**.
""")

user_input = st.chat_input("PRINCE, describe how the DRAGON foiled your rescue attempt this time!")

if user_input:
    with st.spinner("PRINCE, allow me to consult the scrolls of strategy... 🧠 Loading royal tactics..."):
        progress = st.progress(0, text="Analyzing DRAGON's counter-strategy...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Step {i}/5 – Processing wisdom layer {i}...")
            time.sleep(0.5)

        # Prepare the prompt for the Gemini API
        prompt = f"""
You are Gemini, PRINCE's AI strategy advisor. Your job is to respond with a professional and structured rescue review using the following format. Do not include jokes or comical content.

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

        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "max_tokens": 1200,  # Adjust as per Gemini API requirements
            "temperature": 0.7   # Optional: Adjust temperature for response creativity
        }

        response = requests.post(
            gemini_endpoint,
            headers=headers,
            json=data
        )

        try:
            result = response.json()
            full_reply = result.get("response", "⚠️ Gemini didn’t respond properly.")  # Adjust based on Gemini API response structure
        except Exception as e:
            full_reply = f"⚠️ Gemini couldn’t respond properly: {e}\nRaw response: {response.text}"

    # Clean up formatting and remove prompt artifacts
    full_reply = re.sub(r"(?is)you are gemini.*?PRINCE said: \".*?\"", "", full_reply).strip()
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
            st.warning("Gemini didn't include a chart this time.")
