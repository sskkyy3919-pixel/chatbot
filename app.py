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
    return df

df = load_data()
st.title("🏢 المرشد الذكي")

def get_bot_response(user_query, data):
    query = user_query.strip().lower()
    
    # 1. بحث مباشر عن اسم المحل (أولوية)
    for _, row in data.iterrows():
        if str(row['shop_name']).lower() in query:
            return f"📌 **{row['shop_name']}** في **{row['location']}**."

    # 2. بحث ذكي: نفصل المنطق عشان ما يخلط
    matched_shops = []
    for _, row in data.iterrows():
        cat = str(row['category']).lower()
        target = str(row['target_audience']).lower()
        
        # لو المستخدم يبي ملابس أطفال
        if "ملابس" in query and "ملابس" in cat and "اطفال" in target:
            matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
        # لو المستخدم يبي ألعاب
        elif ("العاب" in query or "ترفيه" in query) and "ترفيه" in cat:
            matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
        # لو المستخدم يبي حضانة
        elif "حضانة" in query and "حضانة" in cat:
            matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
            
    if matched_shops:
        return f"✨ إليكِ ما وجدتِ:\n\n" + "\n".join(list(set(matched_shops)))
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

# عرض الأحدث في الأعلى
for user_msg, assistant_msg in reversed([st.session_state.messages[i:i+2] for i in range(0, len(st.session_state.messages), 2)]):
    with st.chat_message(user_msg["role"]): st.markdown(user_msg["content"])
    with st.chat_message(assistant_msg["role"]): st.markdown(assistant_msg["content"])
