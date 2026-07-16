import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="المرشد الذكي", page_icon="🏢", layout="centered")

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

def get_bot_response(user_query, data):
    if data is None: return "⚠️ عذراً، لا يمكنني الوصول للبيانات."
    query = user_query.strip().lower()
    
    # 1. بحث مباشر عن اسم المحل
    for _, row in data.iterrows():
        if str(row['shop_name']).lower() in query or query in str(row['shop_name']).lower():
            return f"📌 **{row['shop_name']}** في **{row['location']}**."

    # 2. بحث مرن (الكل في الكل) - هذا اللي يرجع البوت ذكي
    matched_shops = []
    for _, row in data.iterrows():
        # نجمع كل المعلومات عشان البوت يلقطها
        row_text = f"{row['category']} {row['target_audience']}".lower()
        if any(word in row_text for word in query.split()):
            matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
    
    if matched_shops:
        unique = list(set(matched_shops))
        return f"✨ إليكِ ما وجدتِ:\n\n" + "\n".join(unique)
            
    return "🔍 بحثت لكِ ولم أعثر على ما يطابق طلبكِ!"

if "messages" not in st.session_state: st.session_state.messages = []

def handle_submit():
    if st.session_state.user_query_input:
        query = st.session_state.user_query_input
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": get_bot_response(query, df)})
        st.session_state.user_query_input = "" 

st.text_input("ابحثي هنا...", key="user_query_input", on_change=handle_submit)
st.markdown("---")

# الترتيب: الأحدث دائماً في الأعلى
for i in range(len(st.session_state.messages) - 1, -1, -2):
    if i > 0:
        with st.chat_message(st.session_state.messages[i]["role"]): st.markdown(st.session_state.messages[i]["content"])
        with st.chat_message(st.session_state.messages[i-1]["role"]): st.markdown(st.session_state.messages[i-1]["content"])
