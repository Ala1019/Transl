import pandas as pd
import sqlite3

# ملف الإكسل وملف قاعدة البيانات
EXCEL_FILE = "translations.xlsx"
DB_FILE = "translations.db"

# تحميل البيانات من ملف الإكسل
df = pd.read_excel(EXCEL_FILE)

# فتح الاتصال بقاعدة البيانات
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# التأكد من وجود الجدول
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

# إدخال الصفوف
for _, row in df.iterrows():
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
print("✅ تمت إضافة الترجمات من الإكسل إلى قاعدة البيانات.")
