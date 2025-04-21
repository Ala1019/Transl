
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
    
# ❗️ حذف ملف العلم لإعادة الاستيراد (مرة واحدة فقط)
if os.path.exists("imported.flag"):
    os.remove("imported.flag")

# ✅ Excel Import – this runs once to populate the DB from Excel
if not os.path.exists("imported.flag") and os.path.exists("translations.xlsx"):
    df_excel = pd.read_excel("translations.xlsx")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for _, row in df_excel.iterrows():
        cursor.execute("""
            INSERT INTO translations (title, source_text, style, model, translation, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("title", "Untitled"),
            row["source_text"],
            row.get("style", ""),
            row.get("model", ""),
            row["translation"],
            row.get("notes", ""),
            row.get("status", "")
        ))

    conn.commit()
    conn.close()

    with open("imported.flag", "w") as f:
        f.write("done")

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

if st.button("🧽 إزالة التكرارات"):
    remove_duplicates()
    st.success("✔️ تم حذف التكرارات من قاعدة البيانات.")
    st.rerun()

df = load_translations()
if query:
    df = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
st.dataframe(df)

if st.button("📤 صدّر قاعدة البيانات"):
    with open("translations.db", "rb") as src:
        st.download_button(
            label="📥 حمّل نسخة من قاعدة البيانات",
            data=src,
            file_name="translations.db",
            mime="application/octet-stream"
        )

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
    # 👇 تحميل كل الترجمات المتاحة لتعليم النموذج – بدون تجاوز الحد
    all_translations = load_translations().dropna(subset=["source_text", "translation"])

    examples = ""
    token_count = 0
    max_tokens = 10000  # أو أقل حسب النموذج

    for _, row in all_translations.iterrows():
        en = row["source_text"].strip()
        ar = row["translation"].strip()
        pair = f"English: {en}\nArabic: {ar}\n\n"
        pair_tokens = len(pair.split())

        if token_count + pair_tokens > max_tokens:
            break

        examples += pair
        token_count += pair_tokens


            prompt = f"""You are a professional translator tasked with rendering English texts into Arabic using the user’s personal literary style.

The following examples illustrate the user’s translation style:

{examples}

Now translate the following English text using the same style:

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
if "last_translation" in st.session_state:
    st.subheader("📄 الترجمة الأخيرة:")
    edited = st.text_area("حرر الترجمة إن شئت:", st.session_state["last_translation"], height=200)
    notes = st.text_area("🗒️ ملاحظاتك:")
    status = st.selectbox("⚖️ الحالة:", ["مسوّدة", "بحاجة تنقيح", "جيدة", "نهائية"])

    if st.button("💾 احفظ الترجمة"):
        save_translation(title or "Untitled", input_text, style, model, edited, notes, status)
        st.success("📌 تم الحفظ في قاعدة البيانات.")
