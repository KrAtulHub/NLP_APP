
import streamlit as st
import os
from myapi import API

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="Natural Language Processing Application",
    page_icon="🤖",
    layout="centered"
)

# -----------------------------------
# Custom Styling
# -----------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0f172a;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: bold;
    color: #38bdf8;
    margin-bottom: 10px;
}

.sub-title {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 40px;
}

.stTextArea textarea {
    background-color: #1e293b;
    color: white;
    border-radius: 12px;
    border: 1px solid #334155;
    font-size: 16px;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
}

.stButton button {
    background: linear-gradient(to right, #06b6d4, #3b82f6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 18px;
    width: 100%;
}

.stButton button:hover {
    transform: scale(1.02);
}

.footer {
    text-align: center;
    margin-top: 50px;
    color: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# API Object
# -----------------------------------

try:
    if "HF_TOKEN" in st.secrets and st.secrets["HF_TOKEN"]:
        os.environ["HF_TOKEN"] = str(st.secrets["HF_TOKEN"])
except Exception:
    pass

api = API()

# -----------------------------------
# Header
# -----------------------------------

st.markdown(
    "<div class='main-title'>🤖 Natural Language Processing Application</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub-title'>Artificial Intelligence Powered Text Analysis</div>",
    unsafe_allow_html=True
)

# -----------------------------------
# Feature Selection
# -----------------------------------

feature = st.selectbox(
    "Select Analysis Type",
    [
        "Named Entity Recognition",
        "Emotion Detection"
    ]
)

# -----------------------------------
# Text Input
# -----------------------------------

text = st.text_area(
    "Enter Your Text",
    height=200,
    placeholder="Type your text here..."
)

# -----------------------------------
# Analyze Button
# -----------------------------------

if st.button("Analyze Text"):

    if text.strip() == "":

        st.error("⚠️ Please enter some text")

    else:

        try:

            # -----------------------------------
            # Named Entity Recognition
            # -----------------------------------

            if feature == "Named Entity Recognition":

                result = api.perform_ner(text)

                entities = result.split("\n")

                st.success("✅ Named Entities Detected")

                for entity in entities:

                    if "PER" in entity:
                        st.info(f"👤 {entity}")

                    elif "ORG" in entity:
                        st.info(f"🏢 {entity}")

                    elif "LOC" in entity:
                        st.info(f"📍 {entity}")

                    else:
                        st.info(f"🔹 {entity}")

            # -----------------------------------
            # Emotion Detection
            # -----------------------------------

            elif feature == "Emotion Detection":

                result = api.perform_emotion_detection(text)

                emotion = result['emotion']
                confidence = result['confidence']

                emoji = "😊"

                if emotion.lower() == "sadness":
                    emoji = "😢"

                elif emotion.lower() == "joy":
                    emoji = "😁"

                elif emotion.lower() == "anger":
                    emoji = "😠"

                elif emotion.lower() == "fear":
                    emoji = "😨"

                elif emotion.lower() == "love":
                    emoji = "❤️"

                elif emotion.lower() == "surprise":
                    emoji = "😲"

                st.success(
                    f"{emoji} Detected Emotion: {emotion}"
                )

                st.info(
                    f"📊 Confidence Score: {confidence}"
                )

        except Exception as e:

            st.error(str(e))

# -----------------------------------
# Footer
# -----------------------------------

st.markdown(
    "<div class='footer'>Made with ❤️ using Streamlit and Hugging Face</div>",
    unsafe_allow_html=True
)
