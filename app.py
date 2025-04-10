import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# Page Setup
st.set_page_config(page_title="Rescue Mastermind", layout="wide")
st.title("Rescue Mastermind")
st.caption("Debrief your failed mission. Get strategic, respectful AI guidance for future success.")

# User Input
user_input = st.chat_input("Describe your failed rescue attempt:")

if user_input:
    with st.spinner("Analyzing your strategy..."):
        progress = st.progress(0, text="Processing...")

        for i in range(1, 6):
            progress.progress(i * 20, text=f"Step {i}/5 - Refining insights...")
            time.sleep(0.4)

        # Prompt with structured coaching
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

        # Send request
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

    # Format and clean response
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "")
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply)

    # Extract structured sections
    section_titles = [
        "Summary of Attempt",
        "Why It Failed",
        "What Went Well",
        "Strategic Improvement Plan",
        "Recommended Rescue Idea",
        "Rescue Metrics"
    ]
    extracted_sections = {}
    for i, title in enumerate(section_titles):
        pattern = rf"\[{re.escape(title)}\]\s*(.*?)(?=\n\[{re.escape(section_titles[i + 1])}\]|$)" if i < len(section_titles) - 1 else rf"\[{re.escape(title)}\]\s*(.*)"
        match = re.search(pattern, full_reply, re.DOTALL | re.IGNORECASE)
        extracted_sections[title] = match.group(1).strip() if match else "_Not found_"

    # Tabs
    tab_titles = [
        "📋 Full Report", "📌 Summary", "⚠️ Why It Failed",
        "🌟 What Went Well", "🔧 Improvement Plan",
        "💡 Suggested Strategy", "📊 Rescue Metrics"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.subheader("Full Generated Report")
        st.info("Below is the full unprocessed output from the strategist.")
        st.markdown(full_reply)

    with tabs[1]:
        st.subheader("Summary of Attempt")
        st.success(extracted_sections["Summary of Attempt"])

    with tabs[2]:
        st.subheader("Why It Failed")
        st.error(extracted_sections["Why It Failed"])

    with tabs[3]:
        st.subheader("What Went Well")
        st.success(extracted_sections["What Went Well"])

    with tabs[4]:
        st.subheader("Improvement Plan")
        st.warning(extracted_sections["Strategic Improvement Plan"])

    with tabs[5]:
        st.subheader("Recommended Rescue Idea")
        st.info(extracted_sections["Recommended Rescue Idea"])

    with tabs[6]:
        st.subheader("Performance Metrics")
        chart_section = extracted_sections["Rescue Metrics"]
        chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", chart_section)
        if chart_data:
            labels, values = zip(*[(label.strip(), int(value)) for label, value in chart_data])
            fig, ax = plt.subplots()
            ax.barh(labels, values)
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Rescue Strategy Metrics")
            st.pyplot(fig)
        else:
            st.info("Rescue metrics not found or malformed.")
