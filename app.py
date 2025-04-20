
import streamlit as st
import pandas as pd
import openai
import os

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="My Translator", layout="wide", page_icon="📝")

st.title("📝 My Translator")

# Load translations from CSV
DATA_FILE = "translations.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Title", "Source Text", "Style", "Model", "Translation"])

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
model = st.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4"], index=0)
title = st.text_input("Title for this translation (optional)")

if st.button("Translate"):
    if not input_text.strip():
        st.warning("Please enter some text.")
    else:
        prompt = f"""Translate the following English text into Arabic in the style of {style}:

{input_text}"""
        with st.spinner("Translating..."):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                translated = response.choices[0].message.content.strip()
                st.success("Translation Complete:")
                edited_translation = st.text_area("Edit your translation if needed", translated, height=200)

                if st.button("Save Translation"):
                    new_row = {
                        "Title": title or "Untitled",
                        "Source Text": input_text,
                        "Style": style,
                        "Model": model,
                        "Translation": edited_translation
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Translation saved successfully!")

            except Exception as e:
                st.error(f"Error: {e}")
