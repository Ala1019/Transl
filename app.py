
import streamlit as st
import pandas as pd
import openai
import os

# Load translations
DATA_FILE = "translations.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Title", "Source Text", "Style", "Model", "Translation", "Notes", "Status"])

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="مترجمي الشخصي", layout="wide", page_icon="📘")
st.title("📘 مترجمي الشخصي – بأسلوبك")

st.subheader("🔎 ابحث في ترجماتك")
query = st.text_input("ابحث عن عنوان أو محتوى أو أسلوب")

if query:
    filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
else:
    filtered = df

st.dataframe(filtered)

st.subheader("✍️ تجربة ترجمة جديدة")

title = st.text_input("🔖 عنوان الترجمة")
input_text = st.text_area("النص الإنكليزي", height=200)
style = st.selectbox("اختر الأسلوب", ["Butrus al-Bustani", "al-Jahiz", "Mahmoud Shaker", "أسلوبي الشخصي"])
model = st.selectbox("اختر النموذج", ["gpt-3.5-turbo", "gpt-4"], index=0)

if st.button("ترجم"):
    if not input_text.strip():
        st.warning("الرجاء إدخال النص.")
    else:
        if style == "أسلوبي الشخصي":
            prompt = f"""You are a professional translator. Translate the following English text into Arabic using the user’s personal style, which is defined as follows:

- Language: Elevated, literary, rooted in classical Arabic.
- Voice: Precise, logical, elegant. Avoids journalistic clichés and vague structures.
- Structure: Active voice preferred. Clear rhetorical expression with high fidelity to the original.
- References: Inspired by al-Jahiz, Butrus al-Bustani, Mahmoud Shaker, and the Arab nahda pioneers.
- Sensitivity: Pay special attention to nuances, subtext, and layered meanings in the original text.
- Evaluate word choices based on their connotations in both English and Arabic.
- Be aware of the author’s voice and stylistic intention, and reflect that in the translation.
- Audience: Educated Arabic readers.

Here is the text to translate:

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
                st.success("✅ الترجمة جاهزة")
                edited = st.text_area("حرر الترجمة إن شئت:", translated, height=200)
                notes = st.text_area("🗒️ ملاحظاتك:", "")
                status = st.selectbox("⚖️ الحالة:", ["مسوّدة", "بحاجة تنقيح", "جيدة", "نهائية"])

                if st.button("💾 احفظ الترجمة"):
                    new_row = {
                        "Title": title or "Untitled",
                        "Source Text": input_text,
                        "Style": style,
                        "Model": model,
                        "Translation": edited,
                        "Notes": notes,
                        "Status": status
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("📌 تم الحفظ في الأرشيف.")

            except Exception as e:
                st.error(f"حدث خطأ: {e}")
