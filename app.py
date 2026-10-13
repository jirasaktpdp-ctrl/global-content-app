import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="Global Trends & Content Hub", page_icon="🌍", layout="centered")

st.title("🌍 AI สรุปคอนเทนต์ระดับโลก + รูปภาพ + คำศัพท์ & ลิงก์ต้นฉบับ")
st.write("เลือกหมวดหมู่ ระบบจะดึงบทความทั้งหมด แปลไทย พร้อมรูปภาพ คำศัพท์ และลิงก์ต้นฉบับให้อัตโนมัติ!")

# รวมหมวดหมู่คอนเทนต์
CATEGORY = st.selectbox(
    "📂 เลือกประเภทคอนเทนต์ที่คุณต้องการ:",
    [
        "🔮 ทิศทางโลก & คำทำนายอนาคต (Global Trends & Prophecies)",
        "🚀 เทคโนโลยีล้ำยุค & อนาคต (Futurism)",
        "🌍 เรื่องแปลก / เรื่องน่าทึ่งทั่วโลก (Oddity Central)",
        "🔬 วิทยาศาสตร์ & สิ่งค้นพบใหม่ (Live Science)"
    ]
)

# กำหนดลิงก์ RSS ตามหมวดหมู่ที่เลือก
if "ทิศทางโลก" in CATEGORY:
    selected_url = "https://astrostyle.com/feed/" 
elif "Futurism" in CATEGORY:
    selected_url = "https://futurism.com/feed"
elif "Oddity Central" in CATEGORY:
    selected_url = "https://www.odditycentral.com/feed"
else:
    selected_url = "https://www.livescience.com/feeds/all"

# ฟังก์ชันสกัดคำศัพท์ภาษาอังกฤษน่าสนใจ
def extract_vocab(text, limit=3):
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
        'within', 'without', 'would', 'years', 'content', 'published', 'original', 'appeared', 'astrostyle'
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

# ฟังก์ชันค้นหารูปภาพจาก RSS Item
def extract_image_url(item):
    media_content = item.find('media:content')
    if media_content and media_content.get('url'):
        return media_content.get('url')
    
    enclosure = item.find('enclosure')
    if enclosure and enclosure.get('url') and 'image' in enclosure.get('type', ''):
        return enclosure.get('url')
        
    raw_html = ""
    desc = item.find('description')
    content_encoded = item.find('content:encoded')
    if content_encoded:
        raw_html = content_encoded.text
    elif desc:
        raw_html = desc.text
        
    if raw_html:
        soup_html = BeautifulSoup(raw_html, 'html.parser')
        img_tag = soup_html.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag.get('src')
            
    return None

# ปุ่มกดสั่งดึงข้อมูล
if st.button("🚀 ดึงบทความทั้งหมดจากระบบ", type="primary"):
    with st.spinner("⏳ กำลังเชื่อมต่อระบบดึงข้อมูล รูปภาพ และลิงก์ต้นฉบับ..."):
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
                    st.session_state['feed_items'] = items
                    st.session_state['total_items'] = len(items)
                    st.success(f"✨ ดึงข้อมูลสำเร็จ! พบทั้งหมด {len(items)} บทความในระบบ RSS Feed นี้")

        except Exception as e:
            st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

# หากมีข้อมูลในระบบแล้ว ให้แสดงผลแบบแบ่งหน้า
if 'feed_items' in st.session_state and st.session_state['feed_items']:
    items = st.session_state['feed_items']
    total_items = st.session_state['total_items']
    
    st.markdown("---")
    st.subheader(f"📚 รายการบทความทั้งหมด ({total_items} เรื่อง)")
    
    items_per_page = 5
    total_pages = (total_items - 1) // items_per_page + 1
    
    page = st.selectbox("📄 เลือกหน้าบทความ:", range(1, total_pages + 1), format_func=lambda x: f"หน้า {x} จาก {total_pages} หน้า")
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_items = items[start_idx:end_idx]
    
    translator = GoogleTranslator(source='en', target='th')
    
    count = start_idx + 1
    for item in current_items:
        title = item.find('title')
        link = item.find('link') # ดึงลิงก์ต้นฉบับ
        description = item.find('description')
        content_encoded = item.find('content:encoded')

        title_text = title.text.strip() if title else "ไม่มีหัวข้อ"
        link_text = link.text.strip() if link else "#" # แปลงลิงก์เป็นข้อความ
        
        raw_desc = ""
        if content_encoded:
            raw_desc = content_encoded.text
        elif description:
            raw_desc = description.text

        desc_soup = BeautifulSoup(raw_desc, 'html.parser')
        clean_desc = desc_soup.get_text().strip()

        if len(clean_desc) > 500:
            clean_desc = clean_desc[:500] + "..."
        elif not clean_desc:
            clean_desc = "สรุปเนื้อหาย่อไม่พบข้อมูลเพิ่มเติม"

        img_url = extract_image_url(item)

        # แปลภาษาไทย
        th_title = title_text
        try:
            res_title = translator.translate(title_text)
            if res_title:
                th_title = res_title
        except:
            pass

        th_desc = clean_desc
        try:
            res_desc = translator.translate(clean_desc)
            if res_desc:
                th_desc = res_desc
        except:
            pass

        vocab_items = extract_vocab(f"{title_text} {clean_desc}", limit=3)

        # แสดงผลบนหน้าเว็บ
        st.markdown(f"### 📌 บทความที่ {count}: {th_title}")
        
        if img_url:
            st.image(img_url, use_container_width=True)

        st.markdown(f"**📝 สรุปสาระสำคัญ:**\n{th_desc}")
        
        if vocab_items:
            st.info("💡 **คำศัพท์ภาษาอังกฤษน่าสนใจ:** " + " | ".join([f"**{w}** ({m})" for w, m in vocab_items]))

        # แสดงลิงก์ต้นฉบับ
        st.markdown(f"🔗 **[คลิกเพื่ออ่านบทความต้นฉบับภาษาอังกฤษ]({link_text})**")
        st.markdown("---")
        count += 1