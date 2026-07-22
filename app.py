import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

st.set_page_config(page_title="دليل المول", page_icon="🏢", layout="centered")

# ==========================
# تنسيق الواجهة
# ==========================
st.markdown("""
<style>

.stApp{
    direction:rtl;
    text-align:right;
    background:#f8fafc;
}

h1,p,label{
    text-align:right;
}

.stTextInput input{
    border-radius:12px;
    text-align:right;
}

</style>
""", unsafe_allow_html=True)


# ==========================
# قراءة ملف الاكسل
# ==========================
@st.cache_data
def load_data():

    file_name = "chat_shops.xlsx"

    if not os.path.isfile(file_name):
        return None

    df = pd.read_excel(file_name, engine="openpyxl")

    df.columns = [c.strip().lower() for c in df.columns]

    df["shop_name"] = df["shop_name"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()

    return df


df = load_data()


# إذا الملف غير موجود يتوقف البرنامج
if df is None:
    st.error("⚠️ ملف البيانات غير موجود. تأكد من رفع chat_shops.xlsx")
    st.stop()


# ==========================
# عنوان الصفحة
# ==========================
st.title("🏢 دليل المول")

st.write("🔎 ابحث عن اسم المحل لمعرفة موقعه.")

# ==========================
# مربع البحث
# ==========================
query = st.text_input(
    "",
    placeholder="اكتب اسم المحل هنا..."
)

st.markdown("---")


# ==========================
# البحث
# ==========================
if query:

    query = query.strip()

    shops = df["shop_name"].tolist()

    # تطابق كامل
    exact = df[
        df["shop_name"].str.lower() == query.lower()
    ]

    if not exact.empty:

        shop = exact.iloc[0]["shop_name"]
        location = exact.iloc[0]["location"]

        st.success(f"📍 {shop} يقع في: {location}")

    else:

        # اقتراحات قريبة فقط
        suggestions = get_close_matches(
            query,
            shops,
            n=3,
            cutoff=0.65
        )

        if suggestions:

            st.warning("❌ لم يتم العثور على هذا المحل.")

            st.write("هل تقصد أحد هذه المحلات؟")

            for s in suggestions:

                loc = df[df["shop_name"] == s].iloc[0]["location"]

                st.write(f"• **{s}** — {loc}")

        else:

            st.error("❌ لم يتم العثور على هذا المحل.")
