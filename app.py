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
    
    # 1. بحث عن محل بالاسم (أولوية)
    for _, row in data.iterrows():
        if str(row['shop_name']).lower() in query:
            return f"📌 **{row['shop_name']}** في **{row['location']}**."

    # 2. بحث بالتصنيف (Category) - هذا يحل مشكلة ملابس الأطفال
    matched_shops = []
    
    # تصنيفات واضحة
    for _, row in data.iterrows():
        cat = str(row['category']).lower()
        target = str(row['target_audience']).lower()
        
        # إذا بحث عن ملابس أو ألعاب
        if ("ملابس" in query and "ملابس" in cat) or ("العاب" in query and "ترفيه" in cat):
            if "اطفال" in query: # فلترة إضافية للأطفال
                if "اطفال" in target: matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
            else:
                matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")
        
        # إذا بحث عن حضانة
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
for i in range(0, len(st.session_state.messages), 2):
    with st.chat_message(st.session_state.messages[i]["role"]): st.markdown(st.session_state.messages[i]["content"])
    with st.chat_message(st.session_state.messages[i+1]["role"]): st.markdown(st.session_state.messages[i+1]["content"])
