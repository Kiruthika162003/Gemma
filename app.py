import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re

# Load Hugging Face Token securely from Streamlit
HF_TOKEN = st.secrets["HF_TOKEN"]

st.set_page_config(page_title="Tom's AI Trap Coach", layout="wide")

st.markdown("""
    <h1 style='text-align: center; font-family: monospace;'>TOM'S SMART ASSISTANT – POWERED BY GEMMA</h1>
    <p style='text-align: center; font-style: italic;'>The only thing standing between Jerry and victory... is strategy.</p>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

# Single shared question input
user_input = st.chat_input("Tom, what happened this time? Describe how Jerry escaped!")

if user_input:
    # GEMMA prompt with structure
    prompt = f"""
You are Gemma, Tom's smart assistant. Respond with long, structured, witty output.

1. Start with a motivational message to Tom (with emojis).
2. Identify the episode or trap scenario based on the user's input.
3. Analyze why the trap failed and joke about it.
4. Teach 2-3 strategic lessons Tom should learn.
5. Generate a comic-style description (funny narrative).
6. End with multiple tactical suggestions and a breakdown of Tom's current weaknesses in a chart format like:

   [Chart: Speed=45, Stealth=60, Timing=35, Trap Quality=70, Cheese Placement=50]

Tom said: "{user_input}"
"""

    # Make request to Hugging Face
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"inputs": prompt, "parameters": {"max_new_tokens": 800}}
    response = requests.post("https://api-inference.huggingface.co/models/google/gemma-1.1-7b-it", headers=headers, json=data)

    try:
        full_reply = response.json()[0]['generated_text']
    except:
        full_reply = "Gemma’s thinking got tangled in the mouse trap. Try again."

    # --- Tabs for each section ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💪 Motivation",
        "🎬 Episode Breakdown",
        "📉 Why It Failed",
        "📚 What Tom Should Learn",
        "📊 Tactical Chart"
    ])

    # Parse sections (split by numbered bullet points)
    sections = full_reply.split("\n")

    with tab1:
        st.subheader("Gemma's Words to Hype You Up")
        motivation = next((s for s in sections if s.strip().startswith("1.")), "Gemma’s cheer squad didn’t show up 😅")
        st.markdown(motivation)

    with tab2:
        st.subheader("What Episode Was That?!")
        episode = next((s for s in sections if s.strip().startswith("2.")), "Gemma’s memory skipped the episode 🎞️")
        st.markdown(episode)

    with tab3:
        st.subheader("Here’s Why It Failed…")
        reason = next((s for s in sections if s.strip().startswith("3.")), "Gemma couldn’t figure out the failure 💣")
        st.markdown(reason)

    with tab4:
        st.subheader("Lessons From This Disaster")
        lessons = [s for s in sections if s.strip().startswith("4.") or s.strip().startswith("5.")]
        for lesson in lessons:
            st.markdown(lesson)

    with tab5:
        st.subheader("Gemma’s Tactical Suggestions and Chart")

        tips = [s for s in sections if s.strip().startswith("6.") or "tactic" in s.lower() or "strategy" in s.lower()]
        for t in tips:
            st.markdown(f"✅ {t}")

        # Extract values from chart line
        chart_line = next((s for s in sections if "[Chart:" in s), None)
        st.markdown("---")

        if chart_line:
            st.markdown("**Here’s a chart of Tom’s current weaknesses:**")
            chart_data = re.findall(r"(\w+)=([0-9]+)", chart_line)
            if chart_data:
                labels, values = zip(*[(label, int(value)) for label, value in chart_data])
                fig, ax = plt.subplots()
                ax.barh(labels, values)
                ax.set_xlim(0, 100)
                ax.set_xlabel("Effectiveness (%)")
                st.pyplot(fig)
        else:
            st.warning("Gemma forgot to include the chart data.")

        st.success("Tom, remember — it’s not about chasing harder… it’s about thinking smarter.")
