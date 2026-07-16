import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="المرشد الذكي", page_icon="🏢", layout="centered")

# التنسيق (المنطق الأصلي)
st.markdown("""
    <style>
    .stApp { background-color: #f9fbfd; }
    h1 { color: #2c3e50; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 10px; }
    .stTextInput>div>div>input { border-radius: 25px !important; padding: 12px 20px !important; border: 1px solid #4A90E2 !important; font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "chat_shops.xlsx"
    if not os.path.exists(file_name): return None
    df = pd.read_excel(file_name, engine='openpyxl')
    df.columns = [col.strip().lower() for col in df.columns]
    for col in df.columns:
        if df[col].dtype == 'object': df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()
st.title("🏢 المرشد الذكي")

# دالة البحث الذكي (نفس المنطق القوي اللي اعتمدناه)
def get_bot_response(user_query, data):
    if data is None: return "⚠️ عذراً، لا يمكنني الوصول للبيانات."
    
    query = user_query.strip().lower()
    
    # 1. البحث عن محل محدد
    for _, row in data.iterrows():
        if str(row['shop_name']).lower() in query or query in str(row['shop_name']).lower():
            return f"📌 **{row['shop_name']}** متواجد في **{row['location']}**."

    # 2. البحث الذكي بالتصنيفات
    matched_shops = []
    keywords = {
        "مطعم": "مطاعم", "اكل": "مطاعم", "غدا": "مطاعم", "عشا": "مطاعم",
        "مقهى": "مقاهي", "قهوة": "مقاهي", "كوفي": "مقاهي", "حلا": "حلويات",
        "لبس": "ملابس", "ازياء": "ملابس", "فستان": "ملابس",
        "عبايه": "عبايات", "عبايات": "عبايات",
        "العاب": "ترفيه والعاب", "ترفيه": "ترفيه والعاب", "سينما": "سينما",
        "حضانة": "حضانة", "اطفال": "حضانة"
    }
    
    found_category = None
    for key, val in keywords.items():
        if key in query:
            found_category = val
            break
            
    if found_category:
        for _, row in data.iterrows():
            if found_category in str(row['category']).lower():
                matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
    
    if matched_shops:
        unique = list(set(matched_shops))
        return f"✨ إليكِ ما وجدتِ:\n\n" + "\n".join(unique)
            
    return "🔍 بحثت لكِ ولم أعثر على ما يطابق طلبكِ!"

# إدارة الشات
if "messages" not in st.session_state: st.session_state.messages = []

def handle_submit():
    if st.session_state.user_query_input:
        query = st.session_state.user_query_input
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": get_bot_response(query, df)})
        st.session_state.user_query_input = "" 

st.text_input("اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter...", key="user_query_input", on_change=handle_submit)
st.markdown("---")

# هنا التعديل: عرض الرسائل بترتيبها الطبيعي من القديم للجديد
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
