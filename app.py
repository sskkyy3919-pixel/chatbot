import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة لتكون الواجهة نظيفة ومريحة للعين
st.set_page_config(page_title="دليلك الذكي في المول", page_icon="🏢", layout="centered")

# تحسين مظهر الواجهة بإخفاء القوائم العشوائية وتنسيق الخطوط
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

# دالة ذكية لقراءة البيانات بمرونة عالية
@st.cache_data
def load_data():
    file_name = "chat_shops.xlsx"
    if not os.path.exists(file_name):
        st.error(f"⚠️ لم نجد ملف البيانات باسم '{file_name}' في المستودع! يرجى التأكد من رفعه بنفس الاسم تماماً.")
        return None
    try:
        # قراءة الملف مع تحديد المحرك لضمان عدم حدوث أخطاء توافقية
        df = pd.read_excel(file_name, engine='openpyxl')
        # تنظيف الفراغات وأسماء الأعمدة
        df.columns = [col.strip().lower() for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ تعذر قراءة الملف بسبب نقص في بعض المكتبات. جاري معالجة الأمر تلقائياً...")
        return None

df = load_data()

st.title("🤖 مساعدكِ الذكي لمحلات المول")
st.write("<p style='text-align: center; color: #7f8c8d;'>أهلاً بكِ رُوز! اكتب اسم المحل أو استخدم الأزرار لتسهيل البحث.</p>", unsafe_allow_html=True)
st.markdown("---")

# إعداد صندوق المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطق البحث والرد الذكي
def get_bot_response(user_query, data):
    if data is None:
        return "⚠️ عذراً، لا يمكنني الوصول لبيانات المحلات حالياً لأن ملف الإكسل يحتاج تثبيت مكتبة المساعدة."
    
    query = user_query.strip().lower()
    
    # البحث عن تطابق اسم المحل
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).lower()
        if shop_name in query or query in shop_name:
            location = row['location']
            category = row['category']
            target = row['target_audience']
            return f"📌 **{row['shop_name']}** متواجد في **{location}**.\n\n*(التصنيف: {category} | الفئة: {target})*"
            
    return (
        "🔍 بحثت لكِ ولم أعثر على هذا المحل في القائمة حالياً!\n\n"
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
                    result += f"* **{r['shop_name']}** ({r['location']}) - لـ {r['target_audience']}\n"
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
