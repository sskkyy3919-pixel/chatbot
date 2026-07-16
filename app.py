import streamlit as st
import pandas as pd
import os
import re

# إعدادات الصفحة لتكون الواجهة نظيفة ومريحة للعين
st.set_page_config(page_title="المرشد الذكي", page_icon="🏢", layout="centered")

# تحسين مظهر الواجهة وجعل صندوق الإدخال دائرياً وأنيقاً في الأعلى
st.markdown("""
    <style>
    .stApp {
        background-color: #f9fbfd;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        color: white;
    }
    /* جعل صندوق الكتابة العلوي دائرياً وأنيقاً */
    .stTextInput>div>div>input {
        border-radius: 25px !important;
        padding: 12px 20px !important;
        border: 1px solid #4A90E2 !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# دالة قراءة البيانات بمرونة عالية (المنطق الأصلي)
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

# --- العنوان الفخم ---
st.title("🏢 المرشد الذكي")

# دالة تنظيف الكلمات وإعادتها لأصلها المبسط (المنطق الأصلي)
def clean_and_stem(text):
    text = text.strip().lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    stemmed_words = []
    
    for word in words:
        if word.startswith("ال") and len(word) > 3:
            word = word[2:]
        if (word.startswith("ب") or word.startswith("ل") or word.startswith("و")) and len(word) > 3:
            word = word[1:]
        if word.endswith("ة") or word.endswith("ه"):
            word = word[:-1]
        if word.endswith("ات") and len(word) > 4:
            word = word[:-2]
        elif (word.endswith("ين") or word.endswith("ون")) and len(word) > 4:
            word = word[:-2]
        stemmed_words.append(word)
        
    return stemmed_words

# معجم الترادف الذكي (المنطق الأصلي)
COMMON_SYNONYMS = {
    "كوفي": "مقاهي", "كوفيه": "مقاهي", "قهوه": "مقاهي", "قهوة": "مقاهي", "كافيه": "مقاهي",
    "اكل": "مطاعم", "أكل": "مطاعم", "جوع": "مطاعم", "غدا": "مطاعم", "عشا": "مطاعم",
    "لبس": "ملابس", "ازياء": "ملابس", "أزياء": "ملابس", "فستان": "ملابس", "فساتين": "ملابس"
}

# دالة معالجة الرد الذكية بالكامل (المنطق الأصلي دون تعديل)
def get_bot_response(user_query, data):
    if data is None:
        return "⚠️ عذراً، لا يمكنني الوصول لبيانات المحلات حالياً."
    
    user_words = clean_and_stem(user_query)
    query_flat = " ".join(user_words)
    
    final_search_words = []
    for w in user_words:
        if w in COMMON_SYNONYMS:
            final_search_words.append(COMMON_SYNONYMS[w])
        else:
            final_search_words.append(w)
            
    query_clean_no_spaces = "".join(user_words)
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).strip()
        clean_shop_name = "".join(clean_and_stem(shop_name))
        if clean_shop_name in query_clean_no_spaces or query_clean_no_spaces in clean_shop_name:
            return f"📌 **{shop_name}** متواجد في **{row['location']}**."

    is_food = any(w in final_search_words for w in ["مطاعم", "مطعم", "مَطاعم", "اكل", "أكل"])
    is_cafe = any(w in final_search_words for w in ["مقاهي", "مقهى", "مَقاهي", "كافيه"])
    is_clothing = any(w in final_search_words for w in ["ملابس", "عبايات"])

    if (is_food or is_cafe) and not any(w in user_words for w in ["اين", "وين", "فين"]):
        target_cats = []
        if is_food: target_cats.extend(["مطاعم", "مطعم", "مَطاعم"])
        if is_cafe: target_cats.extend(["مقاهي", "مقهى", "مَقاهي"])
        
        relevant_df = data[data['category'].isin(target_cats)]
        if not relevant_df.empty:
            floors = relevant_df['location'].unique()
            floors_text = " و ".join([f"**{f}**" for f in floors])
            type_text = "المطاعم" if is_food else "الكافيهات والمقاهي"
            return f"🍴 {type_text} متواجدة بالكامل في {floors_text}."

    target_floor = None
    if "ارض" in query_flat or "أرض" in query_flat:
        target_floor = "الارض"
    elif "ثان" in query_flat:
        target_floor = "ثان"
    elif "اول" in query_flat or "أول" in query_flat:
        target_floor = "اول"
    elif "بروم" in query_flat:
        target_floor = "بروم"

    matched_shops = []
    
    target_word = None
    if any(w in user_words for w in ["اطفال", "طفل", "بيبي", "بناتي", "ولادي"]):
        target_word = "أطفال"
    elif any(w in user_words for w in ["نساء", "نسائي", "حريم", "بنات"]):
        target_word = "نساء"
    elif any(w in user_words for w in ["رجال", "رجالي", "شباب"]):
        target_word = "رجال"

    for _, row in data.iterrows():
        cat = str(row['category']).strip()
        target = str(row['target_audience']).strip()
        shop_name = str(row['shop_name']).strip()
        loc = str(row['location']).strip()
        
        cat_roots = clean_and_stem(cat)
        loc_roots = clean_and_stem(loc)
        
        match = False
        
        if target_word and target_word in target:
            has_cat_match = any(w in cat_roots for w in final_search_words if w != "اطفال")
            if has_cat_match:
                match = True
            elif len(final_search_words) <= 2:
                match = True
                
        elif any(w in cat_roots for w in final_search_words):
            match = True
            
        if match:
            if target_floor:
                loc_flat = " ".join(loc_roots)
                if target_floor in loc_flat:
                    matched_shops.append(f"* **{shop_name}** ({loc})")
            else:
                matched_shops.append(f"* **{shop_name}** ({loc})")

    if matched_shops:
        unique_shops = list(set(matched_shops))
        floor_text = f" في الدور المطلوب" if target_floor else ""
        
        if is_food:
            header = f"🍴 **إليكِ المطاعم المتوفرة{floor_text}:**"
        elif is_cafe:
            header = f"☕ **إليكِ الكافيهات والمقاهي المتوفرة{floor_text}:**"
        elif is_clothing:
            header = f"👗 **إليكِ محلات الملابس والعبايات المتوفرة{floor_text}:**"
        elif target_word == "أطفال":
            header = f"👶 **إليكِ المحلات المتوفرة للأطفال{floor_text}:**"
        else:
            header = f"🛍️ **إليكِ المحلات التي تطابق طلبكِ{floor_text}:**"
            
        return f"{header}\n\n" + "\n".join(unique_shops)
            
    return (
        "🔍 بحثت لكِ ولم أعثر على ما يطابق طلبكِ حالياً بالفلترة المطلوبة!\n\n"
        "ولكن يمكنك استخدام **الأزرار التفاعلية بالأسفل** لتصفح الأقسام المتوفرة بكل سهولة 👇"
    )

# تهيئة الذاكرة وحل مشكلة الـ 7 أسئلة
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) > 12:
    st.session_state.messages = st.session_state.messages[2:]

# --- دالة ذكية لإرسال السؤال وتفريغ الصندوق فوراً عند الضغط على Enter ---
def handle_submit():
    query = st.session_state.user_query_input
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        response = get_bot_response(query, df)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.user_query_input = "" # مسح الصندوق بعد الإرسال

# --- وضع مربع الكتابة في الأعلى تماماً تحت العنوان ---
st.text_input(
    "اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter...", 
    key="user_query_input", 
    on_change=handle_submit, 
    placeholder="اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter..."
)

st.markdown("---")

# عرض المحادثات بالأسفل (الأحدث بالأعلى مباشرة تحت مربع الكتابة)
for message in reversed(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- قسم الأزرار التفاعلية المنسقة بالأسفل (المنطق الأصلي) ---
st.markdown("### 🧭 تصفح سريع ومساعد:")
col1, col2, col3 = st.columns(3)

if df is not None:
    with col1:
        if st.button("🍔 المطاعم والمقاهي"):
            food_shops = df[df['category'].isin(['مطاعم', 'مقاهي', 'مَطاعم', 'مَقاهي'])]
            if not food_shops.empty:
                result = "🍴 **المطاعم والمقاهي المتوفرة:**\n"
                for _, r in food_shops.drop_duplicates(subset=['shop_name']).iterrows():
                    result += f"* **{r['shop_name']}** ({r['location']})\n"
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.rerun()

    with col2:
        if st.button("🛍️ الملابس والعبايات"):
            fashion_shops = df[df['category'].isin(['ملابس', 'عبايات'])]
            if not fashion_shops.empty:
                result = "👗 **محلات الملابس والعبايات المتوفرة:**\n"
                for _, r in fashion_shops.drop_duplicates(subset=['shop_name']).iterrows():
                    result += f"* **{r['shop_name']}** ({r['location']})\n"
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.rerun()

    with col3:
        if st.button("🏢 استعراض حسب الأدوار"):
            result = "🏢 **توزيع المحلات حسب الأدوار:**\n\n"
            for floor in df['location'].unique():
                floor_shops = df[df['location'] == floor]['shop_name'].unique()
                result += f"* **{floor}:** {', '.join(floor_shops)}\n"
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.rerun()
