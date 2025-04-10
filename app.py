import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Secure Token and Model
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# App Config
st.set_page_config(page_title="Rescue Mastermind", layout="wide")

# Header
st.title("Rescue Mastermind")
st.caption("Strategic AI insights for your heroic missions")

# User Input
user_input = st.chat_input("Describe your failed rescue attempt:")

if user_input:
    with st.spinner("Analyzing strategy failure..."):
        progress = st.progress(0, text="Gathering tactical insights...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Processing section {i}/5...")
            time.sleep(0.5)

        # Prompt
        prompt = f"""
You are Gemma, PRINCE's AI strategy coach. The prince just attempted a rescue that failed. You must generate a respectful and constructive mission debrief.

Use this exact structure:

[Summary of Attempt]
<Acknowledge the prince’s strategy and effort. Describe what he tried, respectfully.>

[Why It Failed]
<Provide a clear, kind explanation of what didn’t work. Be honest but tactful.>

[What Went Well]
<Highlight any parts of the plan that showed courage, creativity, or progress. Encourage him.>

[Strategic Improvement Plan]
<Give 2–3 action-oriented suggestions to enhance his next rescue attempt. These should sound intelligent, realistic, and valuable.>

[Recommended Rescue Idea]
<Propose one improved plan or rescue approach he could try next time, based on his strengths. Make it clever and practical.>

[Rescue Metrics]
Format as:
[Chart: Courage=70, Timing=45, Magic Usage=30, Rescue Planning=55]

PRINCE said: "{user_input}"
"""

        # API Call
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
            full_reply = f"Gemma could not respond properly: {e}\nRaw response: {response.text}"

    # Clean output
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "")
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply)

    # Extract sections
    sections = {
        "Summary of Attempt": "",
        "Why It Failed": "",
        "What Went Well": "",
        "Strategic Improvement Plan": "",
        "Recommended Rescue Idea": "",
        "Rescue Metrics": ""
    }

    for key in sections:
        match = re.search(rf"\[{re.escape(key)}\](.*?)(?=\n\[|$)", full_reply, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    # Tabs
    tabs = st.tabs([
        "Full Report",
        "Summary",
        "Failure Reason",
        "Highlights",
        "Improvements",
        "Suggestion",
        "Metrics"
    ])

    with tabs[0]:
        st.subheader("Full Strategy Report")
        st.markdown(full_reply)

    with tabs[1]:
        st.subheader("Summary of Attempt")
        st.markdown(sections["Summary of Attempt"] or "_Not available_")

    with tabs[2]:
        st.subheader("Why It Failed")
        st.markdown(sections["Why It Failed"] or "_Not available_")

    with tabs[3]:
        st.subheader("What Went Well")
        st.markdown(sections["What Went Well"] or "_Not available_")

    with tabs[4]:
        st.subheader("Improvement Plan")
        st.markdown(sections["Strategic Improvement Plan"] or "_Not available_")

    with tabs[5]:
        st.subheader("Suggested Strategy")
        st.markdown(sections["Recommended Rescue Idea"] or "_Not available_")

    with tabs[6]:
        st.subheader("Performance Metrics")
        chart_section = sections["Rescue Metrics"]
        if chart_section:
            chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", chart_section)
            if chart_data:
                labels, values = zip(*[(label.strip(), int(value)) for label, value in chart_data])
                fig, ax = plt.subplots()
                ax.barh(labels, values)
                ax.set_xlim(0, 100)
                ax.set_xlabel("Effectiveness (%)")
                ax.set_title("Rescue Performance")
                st.pyplot(fig)
            else:
                st.warning("Could not extract chart data.")
        else:
            st.info("Metrics were not included in the response.")
