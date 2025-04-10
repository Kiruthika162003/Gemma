import streamlit as st
import requests
import re
import time
import matplotlib.pyplot as plt

# Secure API Setup
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# Page Setup
st.set_page_config(page_title="Rescue Mastermind", layout="wide")
st.title("👑 Prince vs Dragon – Rescue Mastermind")
st.caption("AI-powered strategy breakdown for failed heroic missions")

st.markdown("""
Welcome to **Rescue Mastermind** – an AI strategist for your rescue missions.  
Describe your failed rescue attempt and receive:

- A sarcastic yet helpful failure analysis  
- Smart lessons learned  
- Tactical tips  
- A performance breakdown chart

---

💡 **Pro Tip:** Include details like *what you tried*, *how it failed*, and *any funny moment*.
""")

# ---------- HELPERS ---------- #

def extract_section(text, title):
    """Extracts a specific [Title] section from the AI's response."""
    pattern = rf"\[{re.escape(title)}\](.*?)(?=\n\[|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

def display_section(title, content, display_func):
    """Displays a section with fallback."""
    st.markdown(f"## {title}")
    if content:
        display_func(content)
    else:
        st.info(f"No **{title.lower()}** found in this response.")

def display_chart(metrics_text):
    """Parses and displays the rescue metrics as a chart and table."""
    st.markdown("## 📊 Rescue Metrics")
    st.code(f"[Chart:{metrics_text}]" if metrics_text else "No metrics provided.")
    if not metrics_text:
        return

    chart_data = re.findall(r"(Courage|Timing|Magic Usage|Rescue Planning)[\s:=]+(\d+)", metrics_text)
    if chart_data:
        labels, values = zip(*[(label, int(value)) for label, value in chart_data])
        fig, ax = plt.subplots()
        ax.barh(labels, values)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Effectiveness (%)")
        ax.set_title("Tactical Capability Breakdown")
        st.pyplot(fig)

        st.markdown("### 📋 Summary Table")
        st.table({label: [val] for label, val in zip(labels, values)})
    else:
        st.warning("Chart section was found but data could not be extracted.")

# ---------- INPUT ---------- #

user_input = st.chat_input("🗯️ Describe your failed rescue attempt:")

if user_input:
    with st.spinner("Consulting the royal scrolls..."):
        for i in range(1, 6):
            st.progress(i * 20)
            time.sleep(0.3)

        # Prompt with fixed headers
        prompt = f"""
You are Gemma, PRINCE's AI strategy coach. Respond using the following structure and headers:

[Fairytale Guess]
Guess the kind of fairytale or heroic failure this resembles.

[Motivational Quote]
Give a short, funny, or inspiring quote to motivate the prince.

[Why It Failed]
Explain clearly (and sarcastically) why this rescue didn’t work.

[Lessons Learned]
List 2–3 smart lessons the prince should remember.

[Tactical Tips]
Provide 3 actionable tips for future rescue success.

[Rescue Metrics]
Write exactly like this: [Chart: Courage=70, Timing=45, Magic Usage=30, Rescue Planning=55]

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

    # ---------- CLEANING ---------- #
    full_reply = re.sub(r"(?is)you are gemma.*?PRINCE said: \".*?\"", "", full_reply).strip()
    full_reply = re.sub(r"\n{3,}", "\n\n", full_reply).replace("**", "")

    # ---------- EXTRACTION ---------- #
    fairytale = extract_section(full_reply, "Fairytale Guess")
    quote = extract_section(full_reply, "Motivational Quote")
    failure = extract_section(full_reply, "Why It Failed")
    lessons = extract_section(full_reply, "Lessons Learned")
    tips = extract_section(full_reply, "Tactical Tips")
    metrics = extract_section(full_reply, "Rescue Metrics")

    # ---------- DISPLAY ---------- #

    st.markdown("## 📜 Full AI Response")
    st.markdown(full_reply)

    display_section("🧙 Fairytale Guess", fairytale, st.info)
    display_section("💬 Motivational Quote", f"> {quote}" if quote else None, st.success)
    display_section("❌ Why It Failed", failure, st.error)
    display_section("📚 Lessons Learned", lessons, st.success)
    display_section("🛠️ Tactical Tips", tips, st.warning)
    display_chart(metrics)
