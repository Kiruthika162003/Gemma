import streamlit as st
import requests
import matplotlib.pyplot as plt
import re
import time

# Setup
st.set_page_config(page_title="Rescue Mastermind", layout="wide")
st.title("👑 Rescue Mastermind")
st.caption("AI-powered debrief and strategy refinement for heroic missions")

st.markdown("""
Welcome, brave strategist!  
Tell us how your last **rescue attempt** failed, and we’ll analyze your effort, guide your next move, and visualize your tactical profile.

This isn't about winning — it's about **learning like a legend**.
""")

# Input
user_input = st.chat_input("🗯️ What happened in your last rescue attempt?")

if user_input:
    with st.spinner("Consulting the scrolls of wisdom..."):
        for i in range(1, 6):
            st.progress(i * 20, text=f"Processing section {i}/5...")
            time.sleep(0.3)

        # Prompt template
        prompt = f"""
You are Gemma, PRINCE's AI strategy coach. The prince just attempted a rescue that failed. Respond with a respectful, intelligent, and structured debrief.

Format:
[Summary of Attempt]
[Why It Failed]
[What Went Well]
[Strategic Improvement Plan]
[Recommended Rescue Idea]
[Rescue Metrics] — format: [Chart: Courage=70, Timing=45, Magic Usage=30, Rescue Planning=55]

PRINCE said: "{user_input}"
"""

        headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 1000}}

        response = requests.post(
            f"https://api-inference.huggingface.co/models/google/gemma-1.1-7b-it",
            headers=headers,
            json=data
        )

        try:
            result = response.json()
            full_reply = result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            full_reply = f"Error: {e}\nRaw response: {response.text}"

    # Clean output
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply).replace("**", "")

    # Extract sections
    section_titles = [
        "Summary of Attempt", "Why It Failed", "What Went Well",
        "Strategic Improvement Plan", "Recommended Rescue Idea", "Rescue Metrics"
    ]
    extracted = {}
    for i, title in enumerate(section_titles):
        pattern = rf"\[{title}\](.*?)(?=\n\[|$)"
        match = re.search(pattern, full_reply, re.DOTALL)
        extracted[title] = match.group(1).strip() if match else "Not available."

    # 📖 STORY
    st.markdown("## 📖 What the Prince Tried")
    st.markdown(extracted["Summary of Attempt"])

    # ❌ FAILURE
    st.markdown("## ❌ Why It Didn’t Work")
    st.error(extracted["Why It Failed"])

    # 🌟 WINS
    st.markdown("## 🌟 What Went Well")
    st.success(extracted["What Went Well"])

    # 🔧 FIXES
    st.markdown("## 🔧 Strategic Improvement Plan")
    st.warning(extracted["Strategic Improvement Plan"])

    # 💡 SUGGESTION
    st.markdown("## 💡 A Better Rescue Idea")
    st.info(extracted["Recommended Rescue Idea"])

    # 📊 STATS
    st.markdown("## 📊 Rescue Metrics")
    st.markdown(f"```\n{extracted['Rescue Metrics']}\n```")

    chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", extracted["Rescue Metrics"])
    if chart_data:
        labels, values = zip(*[(label, int(val)) for label, val in chart_data])
        fig, ax = plt.subplots()
        ax.barh(labels, values)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Effectiveness (%)")
        ax.set_title("Tactical Performance Breakdown")
        st.pyplot(fig)

        st.markdown("### 🔢 Metric Table")
        st.table({label: [val] for label, val in zip(labels, values)})
    else:
        st.info("No chart data found.")
