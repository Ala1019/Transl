
import streamlit as st
import pandas as pd
import openai
import os

# Load and prepare data
DATA_FILE = "translations.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Title", "Source Text", "Style", "Model", "Translation", "Notes", "Status"])

# Set API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="My Translator – Editor", layout="wide", page_icon="📝")
st.title("📚 مترجمي الشخصي – واجهة التحرير والتحكيم")

st.subheader("📂 الترجمات المخزنة")
search = st.text_input("🔎 ابحث عن ترجمة (بالعنوان أو الكلمات)")

if search:
    filtered_df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
else:
    filtered_df = df

st.dataframe(filtered_df)

st.subheader("✍️ تحرير ترجمة")

selected_index = st.selectbox("اختر رقم الترجمة للتحرير", options=filtered_df.index.tolist() if not filtered_df.empty else [])
if selected_index != "":
    row = df.loc[selected_index]

    st.text("📜 النص الأصلي:")
    st.code(row["Source Text"], language="text")

    new_translation = st.text_area("📝 الترجمة (يمكنك تعديلها):", value=row["Translation"], height=200)
    new_notes = st.text_area("🗒️ ملاحظاتك:", value=row.get("Notes", ""), height=100)
    new_status = st.selectbox("⚖️ تقييم الحالة:", options=["مسوّدة", "بحاجة تنقيح", "جيدة", "نهائية"], index=["مسوّدة", "بحاجة تنقيح", "جيدة", "نهائية"].index(row.get("Status", "مسوّدة")))

    if st.button("💾 حفظ التعديلات"):
        df.at[selected_index, "Translation"] = new_translation
        df.at[selected_index, "Notes"] = new_notes
        df.at[selected_index, "Status"] = new_status
        df.to_csv(DATA_FILE, index=False)
        st.success("✅ تم حفظ التعديلات بنجاح.")
