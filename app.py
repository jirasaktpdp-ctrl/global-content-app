import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="Global Content & Horoscope Hub", page_icon="📱", layout="centered")

st.title("🌟 AI ดึงคอนเทนต์ระดับโลก & ดวงชะตาสากล + คลังคำศัพท์")
st.write("เลือกหมวดหมู่ที่ต้องการ ระบบจะดึงข้อมูล แปลไทย และสกัดคำศัพท์ให้อัตโนมัติ พร้อมนำไปโพสต์ได้ทันที!")

# รวมหมวดหมู่ทั้งหมดไว้ในที่เดียว (ข่าวเทคโนโลยี + เรื่องแปลก + วิทยาศาสตร์ + ดวงชะตา)
CATEGORY = st.selectbox(
    "📂 เลือกประเภทคอนเทนต์ที่คุณต้องการ:",
    [
        "🚀 เทคโนโลยีล้ำยุค & อนาคต (Futurism)",
        "🌍 เรื่องแปลก / เรื่องน่าทึ่งทั่วโลก (Oddity Central)",
        "🔬 วิทยาศาสตร์ & สิ่งค้นพบใหม่ (Live Science)",
        "🔮 ดวงชะตาสากล / โหราศาสตร์โลก (Astrology & Horoscope)"
    ]
)

# กำหนดลิงก์ RSS ตามหมวดหมู่ที่เลือก
if "Futurism" in CATEGORY:
    selected_url = "https://futurism.com/feed"
elif "Oddity Central" in CATEGORY:
    selected_url = "https://www.odditycentral.com/feed"
elif "Live Science" in CATEGORY:
    selected_url = "https://www.livescience.com/feeds/all"
else:
    selected_url = "https://www.astrology.com/horoscope/weekly/general.rss"

# ฟังก์ชันสกัดคำศัพท์ภาษาอังกฤษน่าสนใจ
def extract_vocab(text, limit=4):
    translator = GoogleTranslator(source='en', target='th')
    words = re.findall(r'\b[A-Za-z]{6,}\b', text)
    
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
if st.button("🚀 ดึงข้อมูล 3 เรื่อง + แปลไทย + คำศัพท์น่ารู้", type="primary"):
    with st.spinner("⏳ กำลังเชื่อมต่อระบบ AI ดึงเนื้อหา แปลภาษา และวิเคราะห์ข้อมูล..."):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(selected_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                st.error(f"❌ ไม่สามารถเข้าถึงแหล่งข้อมูลได้ (Code: {response.status_code})")
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
                    for item in items[:3]: # ดึงมาเน้นๆ 3 เรื่อง
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

                        # สกัดคำศัพท์น่ารู้
                        combined_eng_text = f"{title_text} {raw_desc}"
                        vocab_items = extract_vocab(combined_eng_text, limit=4)

                        # แสดงผลเป็นการ์ดคอนเทนต์
                        st.markdown(f"## 📌 เรื่องที่ {count}: {th_title}")
                        st.markdown(f"**📝 เนื้อหา/คำทำนายแปลไทย:**\n{th_desc}")
                        
                        # บล็อกแสดงคำศัพท์น่ารู้
                        if vocab_items:
                            st.info("💡 **คำศัพท์ภาษาอังกฤษน่าสนใจ (Vocabulary Highlights):**")
                            vocab_text = ""
                            for word, meaning in vocab_items:
                                vocab_text += f"• **{word}** = {meaning}\n"
                            st.markdown(vocab_text)

                        st.markdown(f"🔗 [อ่านต้นฉบับภาษาอังกฤษ]({link_text})")
                        st.markdown("---")
                        count += 1

        except Exception as e:
            st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")