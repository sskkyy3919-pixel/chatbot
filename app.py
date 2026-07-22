import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="دليل المول", page_icon="🏢", layout="centered")

# --- تنسيق الواجهة وجعل كل شيء على اليمين (RTL) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f9fbfd;
        direction: rtl;
        text-align: right;
    }
    
    h1, h2, h3, p, label, .stMarkdown {
        text-align: right;
    }
    
    .stTextInput div[data-baseweb="input"] {
        text-align: right;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

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
    # استخدام خانة نصية حرة تتيح للمستخدم الكتابة والضغط على إنتر أو البحث بحرية
    search_query = st.text_input(
        "🔍 ابحث عن اسم المحل لمعرفة موقعه:", 
        placeholder="اكتب اسم المحل هنا واضغط Enter..."
    )
    
    st.markdown("---")
    
    if search_query:
        query_clean = search_query.strip().lower()
        # البحث عن مطابقة تامة أو جزئية للمحل في الإكسل
        result = df[df['shop_name'].str.lower() == query_clean]
        
        if not result.empty:
            loc = result.iloc[0]['location'].strip()
            shop_name_display = result.iloc[0]['shop_name'].title()
            st.success(f" {shop_name_display} يقع في: **{loc}**")
        else:
            st.warning("🔍 لم يتم العثور على موقع هذا المحل.")
else:
    st.error("⚠️ ملف البيانات غير موجود تأكد من رفع ملف 'chat_shops.xlsx'.")
