> R:
import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="مساعد محلات المول الذكي", page_icon="🛍️", layout="centered")

# دالة لقراءة ملف الإكسل بذكاء وأمان
@st.cache_data
def load_data():
    try:
        # قراءة الملف المنظم الذي رفعتِه
        df = pd.read_excel("chat_shops.xlsx")
        # تنظيف الفراغات من أسماء الأعمدة والنصوص لتفادي الأخطاء
        df.columns = [col.strip() for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("عذراً، واجهنا مشكلة في قراءة قاعدة البيانات!")
        return None

df = load_data()

# تصميم واجهة التطبيق اللطيفة
st.title("🤖 مساعدكِ الذكي لمحلات المول")
st.write("أهلاً بك! يمكنك البحث عن موقع أي محل، أو تصفح الأقسام والأدوار بسهولة.")
st.markdown("---")

# إعداد صندوق المحادثة الافتراضي إذا لم يكن موجوداً
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دالة معالجة الرد والبحث المرن
def get_bot_response(user_query, data):
    if data is None:
        return "المعذرة، لا يمكنني الوصول لقائمة المحلات حالياً."
    
    query = user_query.strip().lower()
    
    # 1. البحث المرن عن اسم المحل داخل السؤال
    for _, row in data.iterrows():
        shop_name = str(row['shop_name']).lower()
        if shop_name in query or query in shop_name:
            location = row['location']
            category = row['category']
            target = row['target_audience']
            return f"📌 {row['shop_name']} متواجد في {location}.\n\n*(تصنيف المحل: {category} - الفئة المستهدفة: {target})*"
            
    # 2. الرد البديل والذكي (المنقذ) إذا لم يجد تطابقاً
    return (
        "بحثت لكِ في القائمة ولم أعثر على هذا المحل حالياً! 🔍\n\n"
        "لكن يمكنكِ استخدام الأزرار التفاعلية المساعدة بالأسفل لتصفح المحلات حسب التصنيف أو الأدوار المتوفرة بكل سهولة! 👇"
    )

# استقبال رسائل المستخدم عبر صندوق الشات
if user_input := st.chat_input("اكتب اسم المحل هنا (مثال: سنتربوينت، كودو)..."):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # توليد رد البوت وعرضه
    response = get_bot_response(user_input, df)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# --- قسم الأزرار التفاعلية المساعدة (المنقذة) ---
st.markdown("### 🧭 تصفح سريع ومساعد:")
col1, col2, col3 = st.columns(3)

if df is not None:
    # زر تصفح المطاعم والمقاهي
    with col1:
        if st.button("🍔 المطاعم والمقاهي"):
            food_shops = df[df['category'].isin(['مطاعم', 'مقاهي', 'مَطاعم', 'مَقاهي'])]
            if not food_shops.empty:
                result = "🍴 **المطاعم والمقاهي المتوفرة:**\n"
                for _, r in food_shops.drop_duplicates(subset=['shop_name']).iterrows():
                    result += f"* {r['shop_name']} ({r['location']})\n"
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.rerun()

    # زر تصفح الملابس والعبايات
    with col2:
        if st.button("🛍️ الملابس والعبايات"):
            fashion_shops = df[df['category'].isin(['ملابس', 'عبايات'])]
            if not fashion_shops.empty:
                result = "👗 **محلات الملابس والعبايات المتوفرة:**\n"
                for _, r in fashion_shops.drop_duplicates(subset=['shop_name']).iterrows():
                    result += f"* {r['shop_name']} ({r['location']}) - لـ {r['target_audience']}\n"
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.rerun()

  # زر تصفح الأدوار
with col3:
    if st.button("🏢 استعراض حسب الأدوار"):
        result = "🏢 **توزيع المحلات حسب الأدوار المتوفرة:**\n\n"
        for floor in df['location'].unique():
            floor_shops = df[df['location'] == floor]['shop_name'].unique()
            result += f"* {floor}: {', '.join(floor_shops)}\n"
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()
