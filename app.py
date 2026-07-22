import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="دليل المول", page_icon="🏢", layout="centered")

# --- تنسيق الواجهة وجعل كل شيء والقوائم المنسدلة على اليمين (RTL) ---
st.markdown("""
    <style>
    /* جعل اتجاه الصفحة بالكامل من اليمين لليسار */
    .stApp {
        background-color: #f9fbfd;
        direction: rtl;
        text-align: right;
    }
    
    /* محاذاة العناوين والنصوص إلى اليمين */
    h1, h2, h3, p, label, .stMarkdown {
        text-align: right;
    }
    
    /* محاذاة صندوق الاختيار الرئيسي إلى اليمين */
    .stSelectbox div[data-baseweb="select"] {
        text-align: right;
        direction: rtl;
    }
    
    /* محاذاة القائمة المنسدلة والخيارات التي تظهر عند البحث إلى اليمين */
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
    shop_list.insert(0, "اختر أو ابحث عن المحل...")
    
    selected_shop = st.selectbox("🔍 ابحث عن اسم المحل لمعرفة موقعه:", shop_list)
    
    st.markdown("---")
    
    if selected_shop and selected_shop != "اختر أو ابحث عن المحل...":
        result = df[df['shop_name'].str.lower() == selected_shop.lower()]
        
        if not result.empty:
            loc = result.iloc[0]['location'].strip()
            st.success(f"📌 **{selected_shop}** يقع في: **{loc}**")
        else:
            st.warning("🔍 لم يتم العثور على موقع هذا المحل.")
else:
    st.error("⚠️ ملف البيانات غير موجود تأكد من رفع ملف 'chat_shops.xlsx'.")
