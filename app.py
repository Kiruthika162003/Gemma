import streamlit as st
import requests
import re
import time
import matplotlib.pyplot as plt

# Secure API Setup
HF_TOKEN = st.secrets["HF_TOKEN"]
model_id = "google/gemma-1.1-7b-it"

# Page Setup
st.set_page_config(page_title="Rescue Strategy Review", layout="wide")
st.title("🛡️ Rescue Strategy Review")
st.caption("Assess what worked, what didn't, and how to improve — powered by AI")

st.markdown("""
This tool analyzes your failed rescue mission and delivers a precise strategic review.

🟢 **What Went Well** – Strengths and positives from your effort  
🔴 **What Didn't Work** – Weaknesses or failures in execution  
🔧 **Improved Strategy Plan** – AI-powered upgrades to your next move  
🗺️ **Strategic Map** – A visual breakdown of performance metrics  

Each section provides exactly **5 key points**.
""")

# Input
user_input = st.chat_input("Describe your failed rescue attempt:")

def extract_bullets(section_text):
    if not section_text:
        return ["⚠️ Section not found or empty."]
    bullets = re.findall(r"(?:[-\*]\s+|\n)(.+?)(?=\n|$)", section_text.strip())
    return bullets[:5] if bullets else [section_text.strip()]

def extract_section(text, section):
    pattern = rf"\[{re.escape(section)}\](.*?)(?=\n\[|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

if user_input:
    with st.spinner("Analyzing your strategy..."):
        st.progress(100)
        time.sleep(1)

        prompt = f"""
You are an elite strategy AI assistant. Analyze the PRINCE's failed rescue.
Respond only using the following exact format:

[What Went Well]
List 5 strengths or positive aspects of the attempt.

[What Didn't Work]
List 5 specific problems or reasons it failed.

[Improved Strategy Plan]
List 5 clear changes the PRINCE should make for next time.

[Strategic Map]
Show this exactly like:
[Chart: Courage=65, Timing=40, Magic=25, Planning=50]

PRINCE said: "{user_input}"
"""

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 1000}}

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=data
        )

        try:
            result = response.json()
            full_reply = result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            full_reply = f"Error: {e}\nRaw response: {response.text}"

    # Clean
    full_reply = re.sub(r"(?is)you are.*?PRINCE said: \".*?\"", "", full_reply).strip()

    # Sections
    sections = {
        "What Went Well": extract_bullets(extract_section(full_reply, "What Went Well")),
        "What Didn't Work": extract_bullets(extract_section(full_reply, "What Didn't Work")),
        "Improved Strategy Plan": extract_bullets(extract_section(full_reply, "Improved Strategy Plan")),
        "Strategic Map": extract_section(full_reply, "Strategic Map")
    }

    # Display
    st.markdown("## 🟢 What Went Well")
    for point in sections["What Went Well"]:
        st.success(f"✅ {point}")

    st.markdown("## 🔴 What Didn't Work")
    for point in sections["What Didn't Work"]:
        st.error(f"❌ {point}")

    st.markdown("## 🔧 Improved Strategy Plan")
    for point in sections["Improved Strategy Plan"]:
        st.warning(f"🔄 {point}")

    st.markdown("## 🗺️ Strategic Map")
    chart_text = sections["Strategic Map"]
    st.code(chart_text)

    if chart_text:
        chart_data = re.findall(r"(Courage|Timing|Magic|Planning)[\s:=]+(\d+)", chart_text)
        if chart_data:
            labels, values = zip(*[(label, int(value)) for label, value in chart_data])
            fig, ax = plt.subplots()
            ax.barh(labels, values)
            ax.set_xlim(0, 100)
            ax.set_xlabel("Effectiveness (%)")
            ax.set_title("Strategic Capability Breakdown")
            st.pyplot(fig)

            st.markdown("### 📋 Score Table")
            st.table({label: [val] for label, val in zip(labels, values)})
        else:
            st.warning("Could not extract chart data.")
