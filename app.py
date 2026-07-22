import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="دليل المول", page_icon="🏢", layout="centered")

@st.cache_data
def load_data():
    file_name = "chat_shops.xlsx"
    if not os.path.exists(file_name):
        return None
    df = pd.read_excel(file_name, engine='openpyxl')
    df.columns = [col.strip().lower() for col in df.columns]
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip().str.lower()
    return df

df = load_data()
st.title("🏢 دليل المول")

if df is not None:
    # خانة البحث اللي تتفاعل مع كل حرف يكتبه المستخدم
    search_query = st.text_input("🔍 ابحث عن اسم المحل:", placeholder="اكتب أول حروف من المحل مثل: هوم...")
    
    st.markdown("---")
    
    if search_query:
        # تصفية الجدول بناءً على الحروف المكتوبة (تطابق جزئي)
        query_clean = search_query.strip().lower()
        result_df = df[df['shop_name'].str.contains(query_clean, na=False)]
        
        if not result_df.empty:
            st.success(تم العثور على {len(result_df)} نتيجة:)
            # عرض النتائج بشكل جدول مرتب ونظيف
            for _, row in result_df.iterrows():
                shop = str(row['shop_name']).title()
                loc = str(row['location']).strip()
                st.markdown(f"📌 **{shop}** — موقعها: **{loc}**")
        else:
            st.warning("🔍 لم يتم العثور على محلات تطابق بحثك.")
    else:
        st.info("💡 اكتب أي حرف أو اسم محل في الأعلى ليظهر لك الموقع فوراً.")
else:
    st.error("⚠️ ملف البيانات غير موجود تأكد من رفع ملف 'chat_shops.xlsx'.")
