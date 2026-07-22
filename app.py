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

# --- معجم الترادف الشامل والموسع مع إضافة الحضانة ---
COMMON_SYNONYMS = {

# الملابس
"لبس":"ملابس",
"ملابس":"ملابس",
"تيشيرت":"ملابس",
"بنطلون":"ملابس",
"فستان":"ملابس",
"فساتين":"ملابس",
"جاكيت":"ملابس",

# الرجال
"رجالي":"رجال",
"رجال":"رجال",

# النساء
"نسائي":"نساء",
"نساء":"نساء",
"بنات":"نساء",

# الأطفال
"طفل":"أطفال",
"اطفال":"أطفال",
"بيبي":"أطفال",

# العبايات
"عباية":"عبايات",
"عبايات":"عبايات",

# اللانجري
"لانجري":"لانجري وملابس داخلية",
"بجامة":"لانجري وملابس داخلية",
"ملابس داخلية":"لانجري وملابس داخلية",

# العطور
"عطر":"عطور وتجميل",
"عطور":"عطور وتجميل",
"مكياج":"عطور وتجميل",
"ميكب":"عطور وتجميل",
"كوزمتك":"عطور وتجميل",

# الأحذية
"جزمة":"حقائب و أحذية",
"جزم":"حقائب و أحذية",
"حذاء":"حقائب و أحذية",
"شوز":"حقائب و أحذية",
"بوت":"حقائب و أحذية",
"شنطة":"حقائب و أحذية",
"شنط":"حقائب و أحذية",

# المجوهرات
"ذهب":"اكسسوارات و مجوهرات",
"فضة":"اكسسوارات و مجوهرات",
"اكسسوار":"اكسسوارات و مجوهرات",
"مجوهرات":"اكسسوارات و مجوهرات",

# الساعات
"ساعة":"ساعات",
"ساعات":"ساعات",

# المنزل
"اثاث":"منزل",
"أثاث":"منزل",
"منزل":"منزل",
"كنب":"منزل",
"طاولة":"منزل",

# الرياضة
"رياضة":"رياضة",
"رياضي":"رياضة",
"كورة":"رياضة",
"جيم":"رياضة",

# المطاعم
"مطعم":"مطاعم",
"مطاعم":"مطاعم",
"اكل":"مطاعم",
"غدا":"مطاعم",
"عشا":"مطاعم",
"برجر":"مطاعم",
"بيتزا":"مطاعم",

# المقاهي
"كوفي":"مقاهي",
"قهوة":"مقاهي",
"كافيه":"مقاهي",
"لاتيه":"مقاهي",

# الحلويات
"حلا":"حلويات وايسكريم",
"حلويات":"حلويات وايسكريم",
"آيسكريم":"حلويات وايسكريم",
"ايسكريم":"حلويات وايسكريم",

# السينما
"سينما":"سينما",
"فيلم":"سينما",
"افلام":"سينما",

# الألعاب
"العاب":"ترفيه وألعاب",
"ألعاب":"ترفيه وألعاب",
"ملاهي":"ترفيه وألعاب",

# الصيدليات
"صيدلية":"صيدليات",
"دواء":"صيدليات",
"دوا":"صيدليات",

# السوبرماركت
"سوبرماركت":"سوبرماركت",
"مقاضي":"سوبرماركت",

# الاتصالات
"جوال":"اتصالات",
"شريحة":"اتصالات",
"اتصالات":"اتصالات",

# المحمصة
"محمصة":"محمصة",
"قهوة مختصة":"محمصة"

}
def extract_intent(query):

    query = query.lower()

    intent = {
        "category": None,
        "target": None,
        "floor": None
    }

    # استخراج التصنيف
    for word, category in COMMON_SYNONYMS.items():
        if word in query:
            intent["category"] = category
            break

    # استخراج الفئة
    if any(x in query for x in ["نساء","نسائي","بنات"]):
        intent["target"] = "نساء"

    elif any(x in query for x in ["رجال","رجالي","شباب"]):
        intent["target"] = "رجال"

    elif any(x in query for x in ["اطفال","أطفال","طفل","بيبي"]):
        intent["target"] = "أطفال"

    # استخراج الدور
    if "الأرضي" in query or "ارضي" in query:
        intent["floor"] = "الدور الأرضي"

    elif "الأول" in query:
        intent["floor"] = "الدور الأول"

    elif "الثاني" in query:
        intent["floor"] = "الدور الثاني"

    elif "البروم" in query:
        intent["floor"] = "البروم"

    return intent

# دالة معالجة الرد الذكية بالكامل (المنطق الأصلي دون تعديل)
def get_bot_response(user_query, data):

    if data is None:
        return "⚠️ لا أستطيع قراءة ملف البيانات."

    query = user_query.strip().lower()

    # ==========================
    # أولاً: البحث باسم المحل
    # ==========================

    for _, row in data.iterrows():

        shop = str(row["shop_name"]).strip().lower()

        if shop in query or query in shop:

            return f"📍 **{row['shop_name']}**\n\nيقع في **{row['location']}**."

    # ==========================
    # ثانياً: استخراج نية المستخدم
    # ==========================

    intent = extract_intent(query)

    result = data.copy()

    # ==========================
    # فلترة التصنيف
    # ==========================

    if intent["category"]:

        result = result[
            result["category"].str.strip() == intent["category"]
        ]

    # ==========================
    # فلترة الفئة المستهدفة
    # ==========================

    if intent["target"]:

        result = result[
            result["target_audience"].isin(
                [intent["target"], "الكل"]
            )
        ]

    # ==========================
    # فلترة الدور
    # ==========================

    if intent["floor"]:

        result = result[
            result["location"].str.strip() == intent["floor"]
        ]

    # ==========================
    # لا توجد نتائج
    # ==========================

    if result.empty:
        return "🔍 لم أجد نتائج مطابقة."

    # ==========================
    # ترتيب النتائج
    # ==========================

    shops = result.drop_duplicates(subset=["shop_name"])

    response = "🛍️ **وجدت هذه المحلات:**\n\n"

    for _, row in shops.iterrows():

        response += f"• **{row['shop_name']}** 📍 {row['location']}\n"

    return response

# تهيئة الذاكرة وحل مشكلة الـ 7 أسئلة
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) > 6:
    st.session_state.messages = st.session_state.messages[2:]

# --- دالة الإرسال الذكية ---
def handle_submit():
    query = st.session_state.user_query_input
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        response = get_bot_response(query, df)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.user_query_input = "" 

# --- مربع الكتابة بالأعلى ---
st.text_input(
    "اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter...", 
    key="user_query_input", 
    on_change=handle_submit, 
    placeholder="اكتب اسم المحل أو ما تبحث عنه هنا واضغط Enter..."
)

st.markdown("---")

# عرض المحادثات بالترتيب الصحيح (سؤال فوق وجواب تحت والأحدث بالأعلى)
messages_list = st.session_state.messages
chat_pairs = []

for i in range(0, len(messages_list), 2):
    if i+1 < len(messages_list):
        chat_pairs.append((messages_list[i], messages_list[i+1]))

for user_msg, assistant_msg in reversed(chat_pairs):
    with st.chat_message(user_msg["role"]):
        st.markdown(user_msg["content"])
    with st.chat_message(assistant_msg["role"]):
        st.markdown(assistant_msg["content"])
