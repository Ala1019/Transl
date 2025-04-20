import streamlit as st
import pandas as pd
import openai

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="My Translator", layout="wide", page_icon="📝")

st.title("📝 My Translator")

# Load translations from CSV
df = pd.read_csv("translations.csv")

st.subheader("Search Your Translations")

query = st.text_input("Search by keyword...")

if query:
    filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
else:
    filtered = df

st.dataframe(filtered)

st.subheader("Try a New Translation")

input_text = st.text_area("Enter English text to translate", height=200)
style = st.selectbox("Choose a style", ["Butrus al-Bustani", "al-Jahiz", "Mahmoud Shaker"])
model = st.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4"])

if st.button("Translate"):
    if not input_text.strip():
        st.warning("Please enter some text.")
    else:
        prompt = f"""Translate the following English text into Arabic in the style of {style}:\n\n{input_text}"""
        with st.spinner("Translating..."):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                translated = response.choices[0].message.content.strip()
                st.success("Translation Complete:")
                st.text_area("Your Translation", translated, height=200)
            except Exception as e:
                st.error(f"Error: {e}")
