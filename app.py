import streamlit as st
import requests
import re
import time
import matplotlib.pyplot as plt

# Secure setup
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# UI Layout
st.set_page_config(page_title="Rescue Mastermind", layout="wide")
st.title("👑 Prince vs Dragon – Rescue Mastermind")
st.caption("AI-powered debrief & improvement strategy for failed rescue missions")

st.markdown("""
Welcome to **Rescue Mastermind** – your AI strategist trained to guide heroic efforts.

Describe how your last **rescue attempt failed**, and this app will:
- Generate a structured report
- Analyze why it failed
- Offer strategy lessons
- Suggest smart improvements
- Visualize your tactical strengths

---

💡 **To get the best insights**, include:
- What you tried (e.g. “flew in on a broom”)
- How it went wrong (e.g. “spell fizzled mid-air”)
- Any reactions (e.g. “princess facepalmed”)
""")

# Input
user_input = st.chat_input("🗯️ Tell us what happened in your failed rescue attempt:")

if user_input:
    with st.spinner("Consulting ancient scrolls..."):
        for i in range(1, 6):
            st.progress(i * 20)
            time.sleep(0.3)

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
            full_reply = f"⚠️ Gemma couldn’t respond: {e}\nRaw response: {response.text}"

    # Clean output
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = full_reply.replace("**", "")
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply)

    # --- Display Sections ---
    st.markdown("## 📜 Full Strategy Report")
    st.markdown(full_reply)

    # ❌ Why It Failed
    st.markdown("## ❌ Why It Failed")
    failure_match = re.search(r"(?:3\.|Explain).*?(?:failure|didn’t work).*?\n(.*?)(?:\n\d\.|Teach|Lessons|Tips|List|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
    if failure_match:
        st.error(failure_match.group(1).strip())
    else:
        st.info("No failure breakdown found. Try describing exactly how the attempt failed.")

    # 📚 Lessons Learned
    st.markdown("## 📚 Lessons Learned")
    lessons_match = re.search(r"(?:4\.|Teach).*?(lessons|Learned).*?\n(.*?)(?:\n\d\.|Tips|List|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
    if lessons_match:
        st.success(lessons_match.group(2).strip())
    else:
        st.info("No lessons found. Mention what your plan was to help Gemma analyze it better.")

    # 🛠️ Tactical Tips
    st.markdown("## 🛠️ Tactical Tips")
    tips_match = re.search(r"(?:5\.|Tips|Tactical).*?(List|Improvement).*?\n(.*?)(?:\n\d\.|Chart:)", full_reply, re.DOTALL | re.IGNORECASE)
    if tips_match:
        st.markdown(tips_match.group(2).strip())
    else:
        st.info("Tactical tips not extracted. Help by mentioning what you expected to happen.")

    # 📊 Royal Stats
    st.markdown("## 📊 Royal Stats – Tactical Metrics")
    chart_text_match = re.search(r"Chart:(.*?)(\n\n|$)", full_reply, re.IGNORECASE | re.DOTALL)
    if chart_text_match:
        chart_text = chart_text_match.group(1)
        st.code(f"[Chart:{chart_text.strip()}]")
        chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", chart_text)
        if chart_data:
            labels, values = zip(*[(label, int(val)) for label, val in chart_data])
            fig, ax = plt.subplots()
            ax.barh(labels, values)
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Tactical Capability Breakdown")
            st.pyplot(fig)

            # Optional Table
            st.markdown("### 🧮 Summary Table")
            st.table({label: [val] for label, val in zip(labels, values)})
        else:
            st.warning("Chart structure was found but values couldn't be extracted.")
    else:
        st.info("No tactical metrics were found in Gemma’s response.")
