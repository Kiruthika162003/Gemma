import streamlit as st
import requests
import re
import time
import matplotlib.pyplot as plt

# Load Hugging Face Token securely
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# App setup
st.set_page_config(page_title="Rescue Mastermind", layout="wide")
st.title("👑 Prince vs Dragon – Rescue Mastermind")
st.caption("AI-powered strategy breakdown of your heroic attempts")

st.markdown("""
Welcome to the **Rescue Mastermind**.  
Describe your latest **failed rescue attempt**, and we'll generate a complete breakdown using AI:
- A structured full report
- A witty failure analysis
- Lessons for future success
- Tactical improvement tips
- A performance chart
""")

# User input
user_input = st.chat_input("What happened in your last rescue attempt?")

if user_input:
    with st.spinner("Analyzing your rescue mission..."):
        progress = st.progress(0)
        for i in range(1, 6):
            progress.progress(i * 20)
            time.sleep(0.3)

        # Prompt for AI
        prompt = f"""
You are Gemma, PRINCE's AI coach. Respond ONLY with a structured, witty breakdown:

1. First, guess the fairytale, game level, or heroic failure this resembles. Start with: "Tale Guess: <your guess>"
2. Then give a short epic (or ridiculous) quote to inspire PRINCE.
3. Explain the failure with sarcasm and clarity.
4. Teach PRINCE 2-3 smart rescue lessons.
5. List 3 tactical improvement tips.
6. Finally, give PRINCE's weaknesses in EXACT format:
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

    # Clean output
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply).replace("**", "")

    st.markdown("## 📜 Full Strategy Report")
    st.markdown(full_reply)

    # ❌ Why It Failed
    st.markdown("## ❌ Why It Failed")
    failure = re.search(r"3\..*?Explain.*?\n(.*?)(4\.|Teach|5\.)", full_reply, re.DOTALL | re.IGNORECASE)
    if failure:
        st.error(failure.group(1).strip())
    else:
        st.info("No failure analysis found.")

    # 📚 Lessons Learned
    st.markdown("## 📚 Lessons Learned")
    lessons = re.search(r"4\..*?Teach.*?\n(.*?)(5\.|List|6\.)", full_reply, re.DOTALL | re.IGNORECASE)
    if lessons:
        st.success(lessons.group(1).strip())
    else:
        st.info("No lessons found.")

    # 🛠️ Tactical Tips
    st.markdown("## 🛠️ Tactical Tips")
    tips = re.search(r"5\..*?List 3.*?\n(.*?)(6\.|Finally|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
    if tips:
        st.markdown(tips.group(1).strip())
    else:
        st.info("No tactical tips extracted.")

    # 📊 Royal Stats
    st.markdown("## 📊 Royal Stats – Rescue Metrics")
    weakness_block = re.search(r"Chart:(.*?)(\n\n|$)", full_reply, re.IGNORECASE | re.DOTALL)
    if weakness_block:
        chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", weakness_block.group(1))
        if chart_data:
            labels, values = zip(*[(label.strip(), int(value)) for label, value in chart_data])
            fig, ax = plt.subplots()
            ax.barh(labels, values)
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Rescue Capability Breakdown")
            st.pyplot(fig)

            st.markdown("### Summary Table")
            st.table({label: [val] for label, val in zip(labels, values)})
        else:
            st.warning("Could not extract values for the chart.")
    else:
        st.info("No weaknesses chart found.")
