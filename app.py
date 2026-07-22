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
if df is None:
    st.stop()
st.title("🏢 دليل المول")

if df is not None:

    shop_input = st.text_input(
        "🔍 ابحث عن اسم المحل لمعرفة موقعه:",
        placeholder="اكتب اسم المحل ثم اضغط Enter..."
    )

    if shop_input:

        # البحث عن تطابق كامل
        result = df[df["shop_name"].str.lower() == shop_input.lower()]

        if not result.empty:
            loc = result.iloc[0]["location"]
            st.success(f"📌 **{shop_input.title()}** يقع في **{loc}**")

        else:
            import difflib

            suggestions = difflib.get_close_matches(
                shop_input.lower(),
                df["shop_name"].tolist(),
                n=3,
                cutoff=0.65
            )

            if suggestions:
                st.warning("⚠️ لم يتم العثور على الاسم بالضبط، هل تقصد؟")

                selected = st.selectbox(
                    "اختر المحل:",
                    suggestions,
                    index=None,
                    placeholder="اختر أحد الاقتراحات..."
                )

                if selected:
                    loc = df[df["shop_name"] == selected].iloc[0]["location"]
                    st.success(f"📌 **{selected.title()}** يقع في **{loc}**")

            else:
                st.error("❌ لم يتم العثور على هذا المحل.")
