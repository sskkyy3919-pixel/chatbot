import streamlit as st
import pandas as pd
import os
import re

# إعدادات الصفحة
st.set_page_config(page_title="المرشد الذكي", page_icon="🏢", layout="centered")

# التنسيق
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
    if not os.path.exists(file_name):
        st.error(f"⚠️ لم نجد ملف البيانات باسم '{file_name}' في المستودع!")
        return None
    try:
        df = pd.read_excel(file_name, engine='openpyxl')
        df.columns = [col.strip().lower() for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("⚠️ تعذر قراءة الملف حالياً...")
        return None

df = load_data()
st.title("🏢 المرشد الذكي")

def clean_and_stem(text):
    text = text.strip().lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    stemmed_words = []
    for word in words:
        if word.startswith("ال") and len(word) > 3: word = word[2:]
        if (word.startswith("ب") or word.startswith("ل") or word.startswith("و")) and len(word) > 3: word = word[1:]
        if word.endswith("ة") or word.endswith("ه"): word = word[:-1]
        if word.endswith("ات") and len(word) > 4: word = word[:-2]
        elif (word.endswith("ين") or word.endswith("ون")) and len(word) > 4: word = word[:-2]
        stemmed_words.append(word)
    return stemmed_words

COMMON_SYNONYMS = {
    "كوفي": "مقاهي", "كوفيه": "مقاهي", "قهوه": "مقاهي", "قهوة": "مقاهي", "كافيه": "مقاهي",
    "اكل": "مطاعم", "أكل": "مطاعم", "جوع": "مطاعم", "غدا": "مطاعم", "عشا": "مطاعم", "مطعم": "مطاعم",
    "حلا": "حلويات وآيس كريم", "حلوى": "حلويات وآيس كريم", "ايسكريم": "حلويات وآيس كريم",
    "لبس": "ملابس", "ازياء": "ملابس", "فستان": "ملابس",
    "عبايه": "عبايات", "ملافع": "عبايات",
    "لعب": "ترفيه وألعاب", "العاب": "ترفيه وألعاب", "ألعاب": "ترفيه وألعاب", "ترفيه": "ترفيه وألعاب",
    "حضانه": "حضانة", "بيبي ستر": "حضانة", "رعاية أطفال": "حضانة",
    "علاج": "صيدليات", "دوا": "صيدليات"
}

def get_bot_response(user_query, data):
    if data is None: return "⚠️ عذراً، لا يمكنني الوصول للبيانات."
    user_words = clean_and_stem(user_query)
    query_flat = " ".join(user_words)
    final_search_words = [COMMON_SYNONYMS.get(w, w) for w in user_words]
    
    # مطابقة اسم المحل
    query_clean_no_spaces = "".join(user_words)
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).strip()
        if "".join(clean_and_stem(shop_name)) in query_clean_no_spaces or query_clean_no_spaces in "".join(clean_and_stem(shop_name)):
            return f"📌 **{shop_name}** متواجد في **{row['location']}**."

    # تحديد الفئات
    is_food = any(w in final_search_words for w in ["مطاعم", "مطعم"])
    is_cafe = any(w in final_search_words for w in ["مقاهي", "مقهى"])
    is_clothing = any(w in final_search_words for w in ["ملابس"])
    is_nursery = any(w in final_search_words for w in ["حضانة", "حضانه"])
    is_entertainment = any(w in final_search_words for w in ["ترفيه وألعاب"])

    target_word = "أطفال" if any(w in user_words for w in ["اطفال", "طفل", "بيبي"]) else None
    
    matched_shops = []
    for _, row in data.iterrows():
        cat_roots = clean_and_stem(str(row['category']))
        match = False
        if target_word and target_word == "أطفال" and "اطفال" in str(row['target_audience']):
            match = True
        if any(w in cat_roots for w in final_search_words):
            match = True
            
        if match:
            matched_shops.append(f"* **{row['shop_name']}** ({row['location']})")

    if matched_shops:
        unique = list(set(matched_shops))
        if is_entertainment: header = "🎡 **إليكِ مراكز الترفيه والألعاب المتوفرة:**"
        elif is_nursery: header = "👶 **إليكِ الحضانات ومراكز رعاية الأطفال:**"
        elif target_word == "أطفال": header = "👶 **إليكِ المحلات المتوفرة للأطفال:**"
        else: header = "🛍️ **إليكِ المحلات التي تطابق طلبكِ:**"
        return f"{header}\n\n" + "\n".join(unique)
            
    return "🔍 بحثت لكِ ولم أعثر على ما يطابق طلبكِ!"

if "messages" not in st.session_state: st.session_state.messages = []
def handle_submit():
    if st.session_state.user_query_input:
        st.session_state.messages.append({"role": "user", "content": st.session_state.user_query_input})
        st.session_state.messages.append({"role": "assistant", "content": get_bot_response(st.session_state.user_query_input, df)})
        st.session_state.user_query_input = "" 

st.text_input("اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter...", key="user_query_input", on_change=handle_submit)
st.markdown("---")

for i in range(len(st.session_state.messages) - 1, -1, -2):
    with st.chat_message(st.session_state.messages[i-1]["role"]): st.markdown(st.session_state.messages[i-1]["content"])
    with st.chat_message(st.session_state.messages[i]["role"]): st.markdown(st.session_state.messages[i]["content"])
