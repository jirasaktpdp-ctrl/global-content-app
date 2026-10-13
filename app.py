import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="Global Content & Vocab Learner", page_icon="📚", layout="centered")

st.title("🎬 AI ดึงข่าวแปลก & เทคโนโลยี + คลังคำศัพท์น่ารู้")
st.write("ดึงบทความน่าสนใจ 3 เรื่อง พร้อมแปลไทยและคัดเลือกคำศัพท์ภาษาอังกฤษน่ารู้ให้คุณนำไปทำคอนเทนต์!")

# รายชื่อแหล่งข่าว RSS
SOURCES = {
    "🚀 เทคโนโลยีล้ำยุค & อนาคต (Futurism)": "https://futurism.com/feed",
    "🌍 เรื่องแปลก / เรื่องน่าทึ่งทั่วโลก (Oddity Central)": "https://www.odditycentral.com/feed",
    "🔬 วิทยาศาสตร์ & สิ่งค้นพบใหม่ (Live Science)": "https://www.livescience.com/feeds/all"
}

# สร้างปุ่มเลือกหมวดหมู่บนเว็บ
selected_name = st.selectbox("เลือกแหล่งข้อมูลที่คุณสนใจ:", list(SOURCES.keys()))
selected_url = SOURCES[selected_name]

# ฟังก์ชันสกัดคำศัพท์น่าสนใจจากข้อความภาษาอังกฤษ
def extract_vocab(text, limit=4):
    translator = GoogleTranslator(source='en', target='th')
    # ดึงเฉพาะคำภาษาอังกฤษที่มีความยาวตั้งแต่ 6 ตัวอักษรขึ้นไป (มักจะเป็นคำศัพท์เฉพาะ/คำยากน่าสนใจ)
    words = re.findall(r'\b[A-Za-z]{6,}\b', text)
    
    # คำสามัญทั่วไปที่ไม่ต้องการนำมาแสดง
    stop_words = {
        'about', 'above', 'across', 'after', 'again', 'against', 'almost', 'along', 'already',
        'also', 'always', 'among', 'another', 'around', 'because', 'before', 'behind', 'below',
        'beneath', 'beside', 'between', 'beyond', 'during', 'enough', 'every', 'first', 'found',
        'great', 'however', 'indeed', 'inside', 'itself', 'little', 'making', 'many', 'might',
        'moreover', 'mostly', 'myself', 'never', 'nothing', 'number', 'people', 'rather', 'really',
        'second', 'several', 'should', 'since', 'somebody', 'someone', 'something', 'sometimes',
        'still', 'their', 'themselves', 'there', 'therefore', 'these', 'things', 'think', 'those',
        'though', 'through', 'together', 'under', 'until', 'where', 'whether', 'which', 'while',
        'within', 'without', 'would', 'years', 'content', 'published', 'original', 'appeared'
    }
    
    unique_words = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if w_lower not in stop_words and w_lower not in seen:
            seen.add(w_lower)
            unique_words.append(w_lower)
            if len(unique_words) >= limit:
                break
                
    vocab_list = []
    for word in unique_words:
        try:
            th_meaning = translator.translate(word)
            vocab_list.append((word.capitalize(), th_meaning))
        except:
            pass
            
    return vocab_list

# ปุ่มกดสั่งดึงข้อมูล
if st.button("🚀 ดึงบทความ 3 เรื่อง + แปลไทย + คำศัพท์น่ารู้", type="primary"):
    with st.spinner("⏳ กำลังเชื่อมต่อระบบ AI ดึงเนื้อหา แปลภาษา และวิเคราะห์คำศัพท์..."):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(selected_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                st.error(f"❌ ไม่สามารถเข้าถึงเว็บไซต์ได้ (Code: {response.status_code})")
            else:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                if not items:
                    st.warning("⚠️ ไม่พบข้อมูลบทความในรอบนี้")
                else:
                    translator = GoogleTranslator(source='en', target='th')
                    st.success("✨ ดึงข้อมูล แปลไทย และสกัดคำศัพท์เรียบร้อยแล้ว!")
                    st.markdown("---")

                    count = 1
                    for item in items[:3]: # ดึงมาเน้นๆ 3 บทความ
                        title = item.find('title')
                        link = item.find('link')
                        description = item.find('description')

                        title_text = title.text.strip() if title else "ไม่มีหัวข้อ"
                        link_text = link.text.strip() if link else "#"
                        
                        raw_desc = ""
                        if description:
                            desc_soup = BeautifulSoup(description.text, 'html.parser')
                            raw_desc = desc_soup.get_text().strip()
                            if len(raw_desc) > 400:
                                raw_desc = raw_desc[:400] + "..."

                        # แปลหัวข้อเป็นไทย
                        th_title = title_text
                        try:
                            translated_title = translator.translate(title_text)
                            if translated_title:
                                th_title = translated_title
                        except:
                            pass

                        # แปลเนื้อหาย่อเป็นไทย
                        th_desc = raw_desc
                        if raw_desc:
                            try:
                                translated_desc = translator.translate(raw_desc)
                                if translated_desc:
                                    th_desc = translated_desc
                            except:
                                pass

                        # สกัดคำศัพท์น่ารู้จากหัวข้อ + เนื้อหาภาษาอังกฤษ
                        combined_eng_text = f"{title_text} {raw_desc}"
                        vocab_items = extract_vocab(combined_eng_text, limit=4)

                        # แสดงผลเป็นหน้าการ์ดคอนเทนต์
                        st.markdown(f"## 📌 บทความที่ {count}: {th_title}")
                        st.markdown(f"**📝 เนื้อหาแปลไทย:**\n{th_desc}")
                        
                        # บล็อกแสดงคำศัพท์น่ารู้
                        if vocab_items:
                            st.info("💡 **คำศัพท์ภาษาอังกฤษน่าสนใจในบทความนี้ (Vocabulary Highlights):**")
                            vocab_text = ""
                            for word, meaning in vocab_items:
                                vocab_text += f"• **{word}** = {meaning}\n"
                            st.markdown(vocab_text)

                        st.markdown(f"🔗 [อ่านบทความต้นฉบับภาษาอังกฤษ]({link_text})")
                        st.markdown("---")
                        count += 1

        except Exception as e:
            st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")