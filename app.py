import streamlit as st
import pandas as pd
import os
import re

# إعدادات الصفحة لتكون الواجهة نظيفة ومريحة للعين
st.set_page_config(page_title="دليلك الذكي في المول", page_icon="🏢", layout="centered")

# تحسين مظهر الواجهة
st.markdown("""
    <style>
    .stApp {
        background-color: #f9fbfd;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    </style>
""", unsafe_allow_html=True)

# دالة قراءة البيانات بمرونة عالية
@st.cache_data
def load_data():
    file_name = "chat_shops.xlsx"
    if not os.path.exists(file_name):
        st.error(f"⚠️ لم نجد ملف البيانات باسم '{file_name}' في المستودع!")
        return None
    try:
        df = pd.read_excel(file_name, engine='openpyxl')
        # تنظيف الفراغات وأسماء الأعمدة وتحويلها لحروف صغيرة لسهولة القراءة
        df.columns = [col.strip().lower() for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("⚠️ تعذر قراءة الملف حالياً...")
        return None

df = load_data()

st.title("🤖 مساعدكِ الذكي لمحلات المول")
st.write("<p style='text-align: center; color: #7f8c8d;'>اكتب ما تبحث عنه (مثال: كوفيهات، ملابس أطفال، كودو)...</p>", unsafe_allow_html=True)
st.markdown("---")

# إعداد صندوق المحادثة الافتراضي
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دالة تنظيف الكلمات وإعادتها لأصلها المبسط (Stemming معالجة لغات مبسطة)
def clean_and_stem(text):
    text = text.strip().lower()
    # إزالة علامات الترقيم والرموز
    text = re.sub(r'[^\w\s]', '', text)
    
    words = text.split()
    stemmed_words = []
    
    for word in words:
        # 1. إزالة "ال" التعريف بالبداية
        if word.startswith("ال") and len(word) > 3:
            word = word[2:]
        # 2. إزالة حروف الجر والعطف الملتصقة بالكلمة بالبداية (بـ، لـ، وـ)
        if (word.startswith("ب") or word.startswith("ل") or word.startswith("و")) and len(word) > 3:
            word = word[1:]
        # 3. معالجة التاء المربوطة والهاء في النهاية لتوحيد المطابقة
        if word.endswith("ة") or word.endswith("ه"):
            word = word[:-1]
        # 4. معالجة صيغ الجمع الشائعة (ات، ين، ون)
        if word.endswith("ات") and len(word) > 4:
            word = word[:-2]
        elif (word.endswith("ين") or word.endswith("ون")) and len(word) > 4:
            word = word[:-2]
            
        stemmed_words.append(word)
        
    return stemmed_words

# معجم ذكي داخلي للتحويل التلقائي لبعض الكلمات الدارجة جداً لجذورها المطابقة للإكسل
COMMON_SYNONYMS = {
    "كوفي": "مقاهي", "كوفيه": "مقاهي", "قهوه": "مقاهي", "قهوة": "مقاهي", "كافيه": "مقاهي",
    "اكل": "مطاعم", "أكل": "مطاعم", "جوع": "مطاعم", "غدا": "مطاعم", "عشا": "مطاعم",
    "لبس": "ملابس", "ازياء": "ملابس", "أزياء": "ملابس", "فستان": "ملابس", "فساتين": "ملابس"
}

# دالة معالجة الرد الذكية بالكامل
def get_bot_response(user_query, data):
    if data is None:
        return "⚠️ عذراً، لا يمكنني الوصول لبيانات المحلات حالياً."
    
    # تحويل سؤال المستخدم لجذور كلمات نظيفة
    user_words = clean_and_stem(user_query)
    
    # تبديل الكلمات الدارجة بأصلها المصنف في الإكسل (مثال: كوفيهات -> مقاهي)
    final_search_words = []
    for w in user_words:
        if w in COMMON_SYNONYMS:
            final_search_words.append(COMMON_SYNONYMS[w])
        else:
            final_search_words.append(w)
            
    # 1. البحث أولاً عن تطابق اسم محل محدد
    query_clean_no_spaces = "".join(user_words)
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).strip()
        clean_shop_name = "".join(clean_and_stem(shop_name))
        if clean_shop_name in query_clean_no_spaces or query_clean_no_spaces in clean_shop_name:
            return f"📌 **{shop_name}** متواجد في **{row['location']}**."

    # 2. البحث التلقائي المرن في أعمدة (التصنيف والفئة المستهدفة والاسم) بناءً على جذور الكلمات
    matched_shops = []
    
    # تحديد الفئة المستهدفة من جذور كلمات السؤال (أطفال، نساء، رجال)
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
        
        # استخراج جذور التصنيف والجمهور في الإكسل للمطابقة
        cat_roots = clean_and_stem(cat)
        target_roots = clean_and_stem(target)
        
        match = False
        
        # إذا حدد فئة مستهدفة في السؤال (مثال: أطفال)
        if target_word and target_word in target:
            # إذا حدد كلمة ثانية للتصنيف (مثل: ملابس أطفال)
            has_cat_match = any(w in cat_roots for w in final_search_words if w != "اطفال")
            if has_cat_match:
                match = True
            # إذا كتب فقط "أطفال" أو "حق أطفال"
            elif len(final_search_words) <= 2:
                match = True
                
        # إذا بحث بالمرادفات العامة (مثل: كوفيهات، مطاعم، ملابس)
        elif any(w in cat_roots for w in final_search_words):
            match = True
            
        if match:
            matched_shops.append(f"* **{shop_name}** ({loc})")

    # إذا وجدنا نتائج تطابق البحث بالمنطق
    if matched_shops:
        unique_shops = list(set(matched_shops))
        return f"🛍️ **إليكِ المحلات التي تطابق طلبكِ:**\n\n" + "\n".join(unique_shops)
            
    return (
        "🔍 بحثت لكِ ولم أعثر على ما يطابق طلبكِ حالياً!\n\n"
        "ولكن يمكنك استخدام **الأزرار التفاعلية بالأسفل** لتصفح الأقسام المتوفرة بكل سهولة 👇"
    )

# استقبال الرسائل
if user_input := st.chat_input("اكتب اسم المحل هنا (مثال: سنتربوينت، كودو)..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    response = get_bot_response(user_input, df)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# --- قسم الأزرار التفاعلية المنسقة ---
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
