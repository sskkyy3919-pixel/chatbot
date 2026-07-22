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
    
    .stSelectbox div[data-baseweb="select"] {
        text-align: right;
        direction: rtl;
    }
    
    div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[role="option"] {
        text-align: right !important;
        direction: rtl !important;
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
    shop_list = df['shop_name'].dropna().str.title().unique().tolist()
    
    # استخدام st.selectbox مع السماح بالكتابة الحرة والبحث الفوري
    selected_shop = st.selectbox(
        "🔍 ابحث عن اسم المحل لمعرفة موقعه:", 
        shop_list, 
        index=None, 
        placeholder="ابحث أو اكتب اسم المحل هنا..."
    )
    
    st.markdown("---")
    
    if selected_shop:
        # البحث عن المحل المطابق في ملف الإكسل
        result = df[df['shop_name'].str.lower() == selected_shop.lower()]
        
        if not result.empty:
            loc = result.iloc[0]['location'].strip()
            st.success(f"📌 **{selected_shop}** يقع في: **{loc}**")
        else:
            st.warning("🔍 لم يتم العثور على موقع هذا المحل.")
else:
    st.error("⚠️ ملف البيانات غير موجود تأكد من رفع ملف 'chat_shops.xlsx'.")
