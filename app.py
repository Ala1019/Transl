
import streamlit as st
import pandas as pd
import sqlite3
import openai
import os

# SQLite utility functions
DB_FILE = "translations.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source_text TEXT,
            style TEXT,
            model TEXT,
            translation TEXT,
            notes TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_translations():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM translations", conn)
    conn.close()
    return df

def save_translation(title, source_text, style, model, translation, notes, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO translations (title, source_text, style, model, translation, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, source_text, style, model, translation, notes, status))
    conn.commit()
    conn.close()

def remove_duplicates():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM translations
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM translations
            GROUP BY title, source_text, translation
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit UI
st.set_page_config(page_title="مترجمي الشخصي", layout="wide", page_icon="📘")
st.title("📘 مترجمي الشخصي – SQLite")

# Load and display previous translations
st.subheader("🔎 أرشيف الترجمات")
query = st.text_input("ابحث في الترجمات")

df = load_translations()
if query:
    df = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
st.dataframe(df)

# Translation section
st.subheader("✍️ ترجمة جديدة")

title = st.text_input("🔖 العنوان")
input_text = st.text_area("النص الإنكليزي", height=200)
style = st.selectbox("اختر الأسلوب", ["Butrus al-Bustani", "al-Jahiz", "Mahmoud Shaker", "أسلوبي الشخصي", "أسلوبي الحقيقي"])
model = st.selectbox("اختر النموذج", ["gpt-3.5-turbo", "gpt-4"], index=0)

if st.button("ترجم"):
    if not input_text.strip():
        st.warning("يرجى إدخال نص.")
    else:
        if style == "أسلوبي الحقيقي":
            prompt = f"""You are a professional translator tasked with rendering English texts into Arabic using the user’s personal literary style.

This style is defined by:

- Elevated and classical Arabic language, free from modern journalistic clichés.
- Preference for original Arabic syntax, beginning with the verb where natural.
- Long, rhetorically rich sentences balanced by cadence and logic.
- Imagery-driven narration: metaphor and simile are built progressively and end with poetic force.
- Diction inspired by early 20th-century Arab stylists such as Taha Hussein, Mahmoud Shaker, and Butrus al-Bustani.
- Philosophical and reflective tone; avoids sensationalism and overstatement.
- Sensitive to historical analogy, metaphorical layering, and the connotations of both source and target languages.
- Avoids literal translation when it fails to preserve the author’s tone and subtext.
- Avoid common errors and stylistic weaknesses in Arabic translation.
Be mindful of frequent issues such as passive constructions when the agent is known, weak nominal structures like 'القيام بـ', vague wording, and overly literal phrases that distort the original tone.
- Audience: highly literate Arabic readers.

Translate the following English text into Arabic using this style:

{input_text}
"""
        else:
            prompt = f"""Translate the following English text into Arabic in the style of {style}:

{input_text}"""

        with st.spinner("يتم الترجمة..."):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                translated = response.choices[0].message.content.strip()
                st.session_state["last_translation"] = translated
                st.success("✅ الترجمة جاهزة")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# Show translation output if available
if "last_translation" in st.session_state:
    st.subheader("📄 الترجمة الأخيرة:")
    edited = st.text_area("حرر الترجمة إن شئت:", st.session_state["last_translation"], height=200)
    notes = st.text_area("🗒️ ملاحظاتك:")
    status = st.selectbox("⚖️ الحالة:", ["مسوّدة", "بحاجة تنقيح", "جيدة", "نهائية"])

    if st.button("💾 احفظ الترجمة"):
        save_translation(title or "Untitled", input_text, style, model, edited, notes, status)
        st.success("📌 تم الحفظ في قاعدة البيانات.")
