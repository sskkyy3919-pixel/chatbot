import streamlit as st
import pandas as pd
import os

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
        # تنظيف الفراغات وأسماء الأعمدة
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
st.write("<p style='text-align: center; color: #7f8c8d;'>اكتب اسم المحل أو ما تبحث عنه (مثال: ملابس أطفال، مطعم، سنتربوينت)...</p>", unsafe_allow_html=True)
st.markdown("---")

# إعداد صندوق المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دالة متطورة جداً للبحث المرن بناءً على الاسم، التصنيف، أو الفئة المستهدفة
def get_bot_response(user_query, data):
    if data is None:
        return "⚠️ عذراً، لا يمكنني الوصول لبيانات المحلات حالياً."
    
    # تنظيف نص السؤال بالكامل
    query = user_query.strip().lower()
    clean_query = query.replace(" ", "")
    
    # 1. أولاً: البحث عن اسم محل محدد داخل السؤال (تطابق ذكي)
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).strip()
        clean_shop_name = shop_name.replace(" ", "").lower()
        if clean_shop_name in clean_query or clean_query in clean_shop_name:
            # إذا وجدنا المحل، نرجع موقعه فوراً بدون فلسفة تصنيفات
            return f"📌 **{shop_name}** متواجد في **{row['location']}**."

    # 2. ثانياً: إذا لم يجد اسم محل، يبحث عن الكلمات المفتاحية (مثل: ملابس، أطفال، مطعم، مقهى)
    matched_shops = []
    
    # كلمات مرادفة لتسهيل الفهم
    is_food = any(word in query for word in ["مطعم", "مطاعم", "اكل", "أكل", "جوعان"])
    is_cafe = any(word in query for word in ["مقهى", "مقاهي", "قهوة", "كافيه", "حلى"])
    is_clothing = any(word in query for word in ["ملابس", "محل ملابس", "أزياء", "فساتين"])
    
    # تحديد الفئة المستهدفة من السؤال
    target_word = None
    if "اطفال" in query or "أطفال" in query:
        target_word = "أطفال"
    elif "نساء" in query or "نسائي" in query or "حريمي" in query:
        target_word = "نساء"
    elif "رجال" in query or "رجالي" in query:
        target_word = "رجال"

    for _, row in data.iterrows():
        cat = str(row['category']).strip()
        target = str(row['target_audience']).strip()
        shop_name = str(row['shop_name']).strip()
        loc = str(row['location']).strip()
        
        # تصفية ذكية بناءً على الفئة المستهدفة والتصنيف
        match = False
        
        if target_word and target_word in target:
            if is_clothing and "ملابس" in cat:
                match = True
            elif not is_clothing: # لو طلب بس "أطفال" بدون تحديد نوع المحل
                match = True
        elif is_clothing and "ملابس" in cat:
            match = True
        elif is_food and cat in ["مطاعم", "مطعم", "مَطاعم"]:
            match = True
        elif is_cafe and cat in ["مقاهي", "مقهى", "مَقاهي"]:
            match = True
            
        if match:
            matched_shops.append(f"* **{shop_name}** ({loc})")

    # إذا وجدنا محلات تطابق البحث العام
    if matched_shops:
        # إزالة التكرار
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
