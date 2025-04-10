import streamlit as st
import requests
import os
import matplotlib.pyplot as plt
import re
import time

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

st.set_page_config(page_title="Prince vs Dragon Rescue Mastermind", layout="wide")

st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-family:monospace; font-size: 3em;'>👑 PRINCE VS DRAGON RESCUE MASTERMIND</h1>
        <p style='font-style: italic; font-size: 1.2em;'>Powered by Gemma 3 — Your heroic AI strategy assistant</p>
    </div>
    <hr style="margin-bottom: 30px;">
""", unsafe_allow_html=True)

st.markdown("""
> 🐉 The prince has tried for decades — swords, spells, catapults… always eaten.  
> But what if **AI** could finally help him rescue the princess?  
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
You are Gemma, PRINCE's AI coach. Respond ONLY with a structured, witty breakdown:

1. First, guess the fairytale, game level, or heroic failure this resembles. Start with: "Tale Guess: <your guess>"
2. Then give a short epic (or ridiculous) quote to inspire PRINCE (use emojis).
3. Explain the failure with humor, flair, and royal sarcasm.
4. Teach PRINCE 2-3 clever rescue lessons.
5. Write a short comic-narration of the failed rescue.
6. List 3 tactical improvement tips.
7. Finally, give PRINCE's weaknesses in EXACT format:
   [Chart: Courage=45, Timing=50, Magic Usage=35, Rescue Planning=60]

DO NOT skip the chart. Always end with it.
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

    # Clean up formatting
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "").strip()

    # Subtabs for sectioned display
    tabs = st.tabs([
        "🧾 Full Response",
        "🔍 Rescue Analysis",
        "💬 Quote of the Quest",
        "❌ Why It Failed",
        "📚 Lessons Learned",
        "🛠️ Tactical Tips",
        "📊 Royal Stats"
    ])

    with tabs[0]:
        st.markdown(full_reply)

    with tabs[1]:
        st.markdown("### 🔍 Comic-Narration of the Failed Rescue")
        narration = re.search(r"(5\..*?narration.*?:\s*)(.*?)(\n6\.|\nList 3|\n7\.|Finally|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
        if narration:
            st.markdown(narration.group(2).strip())
        else:
            st.warning("Could not extract the rescue narration. Try including how the escape looked.")

    with tabs[2]:
        st.markdown("### 💬 Gemma's Motivational Quote")
        quote_match = re.search(r"2\..*?(?:(?:inspire PRINCE)|(?:quote)).*?\n+(.*?)\n", full_reply, re.DOTALL | re.IGNORECASE)
        if quote_match:
            st.markdown(f"> *{quote_match.group(1).strip()}*")
        else:
            st.warning("No quote found. Include a mood in your prompt for more flair!")

    with tabs[3]:
        st.markdown("### ❌ Analysis of the Failure")
        fail_match = re.search(r"3\..*?Explain.*?\n+(.*?)(\n4\.|Teach|5\.)", full_reply, re.DOTALL | re.IGNORECASE)
        if fail_match:
            st.markdown(fail_match.group(1).strip())
        else:
            st.warning("Failure analysis missing. Try to describe what failed in your attempt.")

    with tabs[4]:
        st.markdown("### 📚 Rescue Lessons for Next Time")
        lessons_match = re.search(r"4\..*?Teach.*?\n+(.*?)(\n5\.|Write|6\.)", full_reply, re.DOTALL | re.IGNORECASE)
        if lessons_match:
            st.markdown(lessons_match.group(1).strip())
        else:
            st.warning("Gemma didn't generate rescue lessons this time.")

    with tabs[5]:
        st.markdown("### 🛠️ Tactical Tips")
        tips_match = re.search(r"6\..*?List 3.*?\n+(.*?)(\n7\.|Finally|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
        if tips_match:
            st.markdown(tips_match.group(1).strip())
        else:
            st.warning("Tips not found. Try asking for specific help in your prompt.")

    with tabs[6]:
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
            st.warning("Gemma didn’t provide a weaknesses chart.")
