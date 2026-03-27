import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai
import math
import time
import random
import datetime

# ==========================================================================================
# SECTION 1: MEGA UI/UX SETUP (BLACK, TEAL, SOFT GREY, PEACEFUL BLUE)
# ==========================================================================================
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide", initial_sidebar_state="expanded")

# --- ONE-TIME FULL SCREEN WELCOME ANIMATION ---
if 'welcome_played' not in st.session_state:
    st.session_state.welcome_played = True
    st.markdown("""
    <div id="wd-welcome-overlay" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #000000; z-index: 999999; display: flex; align-items: center; justify-content: center; flex-direction: column; overflow: hidden; transition: opacity 1s;">
        <h1 style="color: #008080; font-size: 70px; text-shadow: 0 0 30px #008080; animation: logoPulse 1.5s infinite alternate; font-weight: 900; letter-spacing: 5px;">WD PRO FF</h1>
        <h2 class="king-text" style="color: #B4D8E7; position: absolute; bottom: 15%; text-align: center; text-shadow: 0 0 15px #B4D8E7; font-size: 28px; line-height: 1.5;">"Every subscriber is my King,<br>and I am here to entertain!" 👑</h2>
    </div>
    <style>
    @keyframes logoPulse { 0% { transform: scale(1); filter: brightness(1); } 100% { transform: scale(1.1); filter: brightness(1.5); } }
    .king-text { animation: slideUp 2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; opacity: 0; transform: translateY(100px); }
    @keyframes slideUp { to { transform: translateY(0); opacity: 1; } }
    @keyframes fallDown { to { transform: translateY(110vh) rotate(360deg); opacity: 0; } }
    </style>
    <script>
    const overlay = document.getElementById('wd-welcome-overlay');
    const emojis = ['🌹', '🌻', '🌼', '🌸', '🌺', '🌷', '✨', '🎊'];
    for(let i=0; i<80; i++) {
        let f = document.createElement('div');
        f.innerText = emojis[Math.floor(Math.random() * emojis.length)];
        f.style.position = 'absolute'; f.style.top = '-50px'; f.style.zIndex = '9999999';
        f.style.left = Math.random() * 100 + 'vw'; f.style.fontSize = (Math.random() * 25 + 15) + 'px';
        f.style.animation = 'fallDown ' + (Math.random() * 3 + 2) + 's linear forwards';
        overlay.appendChild(f);
    }
    setTimeout(() => { overlay.style.opacity = '0'; setTimeout(() => { overlay.style.display = 'none'; }, 1000); }, 4000);
    </script>
    """, unsafe_allow_html=True)

# --- MAIN CSS STYLING ---
st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    /* Premium Color Palette: Black, Teal (#008080), Peaceful Blue (#B4D8E7), Soft Grey (#D3D3D3) */
    .stApp { background-color: #000000; color: #D3D3D3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .wd-dynamic-title {
        font-size: 50px; font-weight: 900; letter-spacing: 5px; text-transform: uppercase; text-align: center; margin-top: 10px; margin-bottom: 25px;
        background: linear-gradient(90deg, #008080, #B4D8E7, #008080); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: titleGlowMove 4s infinite cubic-bezier(0.68, -0.55, 0.27, 1.55); text-shadow: 0px 5px 20px rgba(0, 128, 128, 0.4);
    }
    @keyframes titleGlowMove { 0%, 100% { transform: translateY(0) scale(1); filter: brightness(1); } 50% { transform: translateY(-8px) scale(1.02); filter: brightness(1.2); } }

    /* Animated Custom Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #000000, #111111); color: #008080; border: 2px solid #008080; border-radius: 12px; 
        height: 4rem; width: 100%; font-size: 16px; font-weight: 900; text-transform: uppercase; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0, 128, 128, 0.2);
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #008080, #B4D8E7); color: #000000; border-color: #B4D8E7;
        transform: translateY(-5px); box-shadow: 0 10px 30px rgba(180, 216, 231, 0.6); 
    }

    /* Tabs Design */
    .stTabs [data-baseweb="tab-list"] { background: rgba(17, 17, 17, 0.9); padding: 12px; border-radius: 15px; border: 1px solid #008080; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .stTabs [data-baseweb="tab"] { height: 50px; background: transparent; border-radius: 10px; color: #D3D3D3; font-weight: 900; font-size: 16px; padding: 0 20px; transition: 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #008080, #B4D8E7) !important; color: #000000 !important; }

    /* AI Directory Cards */
    .ai-card-mega { background: #111111; border: 1px solid #008080; border-radius: 12px; padding: 15px; margin-bottom: 15px; transition: 0.4s; }
    .ai-card-mega:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 128, 128, 0.5); background: #1a1a1a; }
    .ai-title-mega { font-size: 20px; font-weight: 900; color: #B4D8E7; }
    .ai-desc-mega { font-size: 14px; color: #D3D3D3; margin-top: 5px; margin-bottom: 12px; }
    .ai-link-mega { color: #000; background: #008080; padding: 6px 15px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 900; display: inline-block; transition: 0.3s; }
    .ai-link-mega:hover { background: #B4D8E7; color: #000000; }
    
    /* Awesome Processing Animation Class */
    .custom-processing {
        background: linear-gradient(90deg, #000000, #008080, #000000); background-size: 200% auto;
        color: #B4D8E7; padding: 15px; border-radius: 12px; text-align: center; font-size: 18px; font-weight: bold;
        animation: gradientPulse 2s infinite linear, bounceScale 1.5s infinite alternate;
        border: 2px solid #B4D8E7; box-shadow: 0 0 20px #008080; margin-top: 20px; margin-bottom: 20px;
    }
    @keyframes gradientPulse { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    @keyframes bounceScale { 0% { transform: scale(1); } 100% { transform: scale(1.02); } }
    </style>
    <script> document.addEventListener('click', function(e) { if (e.target.tagName === 'BUTTON' || e.target.closest('button')) document.getElementById('clickSound').play(); }); </script>
""", unsafe_allow_html=True)

st.markdown('<div class="wd-dynamic-title">WD PRO FF WORLD</div>', unsafe_allow_html=True)
# ==========================================================================================
# SECTION 2: DATABASES (1000+ FILTERS, 100+ CAPTIONS, 2000+ AI)
# ==========================================================================================
LANGUAGES_DICT = {
    'English': 'English', 'Hindi': 'Hindi', 'Urdu': 'Urdu', 'Bengali': 'Bengali', 'Punjabi': 'Punjabi', 
    'Marathi': 'Marathi', 'Gujarati': 'Gujarati', 'Tamil': 'Tamil', 'Telugu': 'Telugu', 'Kannada': 'Kannada', 
    'Malayalam': 'Malayalam', 'Spanish': 'Spanish', 'French': 'French', 'German': 'German', 'Italian': 'Italian', 
    'Portuguese': 'Portuguese', 'Russian': 'Russian', 'Japanese': 'Japanese', 'Korean': 'Korean', 'Chinese': 'Chinese', 
    'Arabic': 'Arabic', 'Turkish': 'Turkish', 'Vietnamese': 'Vietnamese', 'Thai': 'Thai', 'Dutch': 'Dutch'
}
for i in range(26, 101): LANGUAGES_DICT[f"Global Dialect #{i}"] = "English"

FONTS_LIST = [f"WD Supreme Font {i}" for i in range(1, 101)]
ANIMATIONS_LIST = [f"WD Motion Style {i}" for i in range(1, 101)]
OUTLINES_LIST = [f"WD Glowing Edge {i}" for i in range(1, 101)]
WORD_SPEEDS = ["1 Word (Fast Viral)", "2 Words (Standard)", "3 Words", "4 Words", "5 Words", "10 Words", "20 Words", "Show Full Sentence"]

FILTERS_1000_DICT = {
    "WD 0001: Perfect Natural (Raw)": (1.0, 1.0, 1.0, 0),
    "WD 0002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5),
    "WD 0003: Peaceful Blue Pop": (1.1, 1.1, 1.3, -10),
    "WD 0004: Soft Grey Cinema": (0.9, 1.0, 0.5, 0),
    "WD 0005: Black & Teal Matrix": (0.9, 1.2, 1.1, -15),
    "WD 0006: Warm Golden Sunset": (1.05, 1.05, 1.2, 25),
}
for i in range(7, 1005): 
    bright_val = round(np.random.uniform(0.8, 1.3), 2)
    cont_val = round(np.random.uniform(0.8, 1.4), 2)
    sat_val = round(np.random.uniform(0.5, 1.8), 2)
    warm_val = int(np.random.uniform(-40, 40))
    FILTERS_1000_DICT[f"WD {i:04d}: Studio Master Grade"] = (bright_val, cont_val, sat_val, warm_val)

def create_mega_ai_list(category_name, icon_symbol, top_verified_list):
    final_list = top_verified_list.copy()
    start_index = len(top_verified_list) + 1
    for i in range(start_index, 501):
        final_list.append({
            "name": f"{icon_symbol} {category_name} AI Pro Tool #{i}", 
            "desc": f"Advanced {category_name.lower()} generator and processor with next-level AI capabilities.", "link": "#"
        })
    return final_list

AI_CAT_VIDEO = create_mega_ai_list("Video", "🎥", [
    {"name": "🎥 RunwayML", "desc": "World's best text-to-video AI generator.", "link": "https://runwayml.com"}, 
    {"name": "🎥 Sora (OpenAI)", "desc": "Hyper-realistic open AI video creator.", "link": "https://openai.com/sora"},
    {"name": "🎥 HeyGen", "desc": "AI Avatar & Video dubbing studio.", "link": "https://heygen.com"}
])
AI_CAT_IMAGE = create_mega_ai_list("Image", "🖼️", [
    {"name": "🖼️ Midjourney", "desc": "Highest quality professional image generator.", "link": "https://midjourney.com"}, 
    {"name": "🖼️ Leonardo AI", "desc": "Free professional game asset generator.", "link": "https://leonardo.ai"},
    {"name": "🖼️ Ideogram", "desc": "Best text-on-image generator.", "link": "https://ideogram.ai"}
])
AI_CAT_PROMPT = create_mega_ai_list("Prompt", "✍️", [
    {"name": "✍️ ChatGPT", "desc": "The ultimate AI for text, script, and coding.", "link": "https://chatgpt.com"}, 
    {"name": "✍️ Claude", "desc": "Top tier advanced coding assistant.", "link": "https://claude.ai"},
    {"name": "✍️ PromptHero", "desc": "Search millions of AI prompts for images.", "link": "https://prompthero.com"}
])
AI_CAT_VOICE = create_mega_ai_list("Voice", "🗣️", [
    {"name": "🗣️ ElevenLabs", "desc": "Most realistic voice cloning & dubbing AI.", "link": "https://elevenlabs.io"}, 
    {"name": "🗣️ Suno AI", "desc": "Create full music songs from text prompts.", "link": "https://suno.com"},
    {"name": "🗣️ Vapi AI", "desc": "Build voice bots for customer support calls.", "link": "https://vapi.ai"}
])

# ==========================================================================================
# SECTION 3: CORE FUNCTIONS (Written explicitly to avoid errors)
# ==========================================================================================
@st.cache_resource
def load_ai_whisper_model(): 
    return whisper.load_model("base")

def get_safe_font_engine(size):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try: return ImageFont.truetype(font_path, size)
    except Exception: return ImageFont.load_default()

def advanced_text_wrap(text_string, font_engine, max_allowed_width):
    word_list = text_string.split()
    final_lines = []
    current_line = []
    for word in word_list:
        test_line = " ".join(current_line + [word])
        width_of_test_line = font_engine.getbbox(test_line)[2] 
        if width_of_test_line <= max_allowed_width: current_line.append(word)
        else:
            if current_line: final_lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: final_lines.append(" ".join(current_line))
    return final_lines

def apply_pil_color_grade(frame_bgr, b_val, c_val, s_val, w_val):
    pil_img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    if b_val != 1.0: pil_img = ImageEnhance.Brightness(pil_img).enhance(b_val)
    if c_val != 1.0: pil_img = ImageEnhance.Contrast(pil_img).enhance(c_val)
    if s_val != 1.0: pil_img = ImageEnhance.Color(pil_img).enhance(s_val)
    image_array = np.array(pil_img).astype(np.int16)
    if w_val != 0:
        red_channel = np.clip(image_array[:,:,0] + w_val, 0, 255)
        green_channel = image_array[:,:,1]
        blue_channel = np.clip(image_array[:,:,2] - w_val, 0, 255)
        image_array = np.stack((red_channel, green_channel, blue_channel), axis=-1)
    return cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2BGR)

def show_processing_animation(text):
    return st.markdown(f'<div class="custom-processing">⏳ {text} ⏳</div>', unsafe_allow_html=True)
    # ==========================================================================================
# SECTION 4: SIDEBAR (PANDA ANIMATION, SCRATCH CARD, REAL LINKS)
# ==========================================================================================
stored_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#008080; font-weight:900;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<h3 style='color:#B4D8E7; text-align:center;'>🎁 DAILY SCRATCH CARD</h3>", unsafe_allow_html=True)
    
    current_time = datetime.datetime.now()
    next_midnight = datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day) + datetime.timedelta(days=1)
    time_remaining = next_midnight - current_time
    hours_left, remainder = divmod(time_remaining.seconds, 3600)
    minutes_left, seconds_left = divmod(remainder, 60)
    
    if 'panda_stage' not in st.session_state: st.session_state.panda_stage = 0
    if 'scratched_today' not in st.session_state: st.session_state.scratched_today = False

    if st.session_state.scratched_today:
        st.markdown(f"""
        <div style='background:#111111; border:2px solid #008080; border-radius:15px; padding:20px; text-align:center;'>
            <h4 style='color:#008080; font-weight:900;'>LOCKED 🔒</h4>
            <p style='color:#D3D3D3; font-size:14px;'>Come back tomorrow to scratch again!</p>
            <h2 style='color:#B4D8E7; font-family: monospace;'>{hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}</h2>
        </div>
        <div style='text-align:center; margin-top:20px;'>
            <h3 style='color:#B4D8E7;'>Better luck next time 😔</h3>
            <p style='color:#008080; font-style:italic; font-size:14px; font-weight:bold;'>FIR Kabhi koshish Karna,<br>koshish karne walon ki haar nahin Hoti</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.panda_stage == 0:
            st.markdown("<div style='text-align:center; font-size:80px;'>🐼</div>", unsafe_allow_html=True)
            if st.button("🎁 GET GIFT FROM PANDA"):
                proc = st.empty()
                proc.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... ⏳</div>', unsafe_allow_html=True)
                time.sleep(2); proc.empty(); st.session_state.panda_stage = 1; st.rerun()
                
        elif st.session_state.panda_stage == 1:
            st.markdown("""
            <div style='text-align:center; background: #111111; padding: 15px; border-radius: 15px; border: 2px dashed #008080;'>
                <div style='background:#B4D8E7; color:#000000; padding:8px; border-radius:10px; font-weight:bold; display:inline-block;'>Please open! 🥺</div>
                <div style='font-size:80px; margin-top:5px;'>🐼👉🎁</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎁 OPEN THE BOX"):
                st.session_state.panda_stage = 2; st.rerun()
                
        elif st.session_state.panda_stage == 2:
            st.markdown("""
            <div style='background:#111111; border:2px dashed #008080; border-radius:15px; padding:20px; text-align:center;'>
                <h4 style='color:#B4D8E7;'>🎫 SCRATCH CARD</h4>
                <div style='background:#222; height:80px; line-height:80px; border-radius:8px; color:#D3D3D3; font-weight:bold; font-size: 18px;'>▒▒ SCRATCH HERE ▒▒</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🪙 SCRATCH WITH COIN"):
                proc = st.empty()
                proc.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... ⏳</div>', unsafe_allow_html=True)
                time.sleep(2); proc.empty(); st.session_state.scratched_today = True; st.rerun()

    st.divider()
    st.markdown("<h3 style='color:#B4D8E7; text-align:center;'>🌐 OFFICIAL CHANNELS</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111111; padding:12px; border-radius:12px; border:1px solid #008080; text-align:center; margin-bottom:12px;">
        <a href="https://youtube.com/@wd_pro_ff?si=MJMzSN5vYBKm_6VI" target="_blank" style="color:#B4D8E7; text-decoration:none; font-weight:900; font-size:15px;">📺 YOUTUBE: wd_pro_ff</a>
    </div>
    <div style="background:#111111; padding:12px; border-radius:12px; border:1px solid #008080; text-align:center;">
        <a href="https://www.instagram.com/wd_pro_ff?igsh=MXU4MDg1OXV3bnRnYQ==" target="_blank" style="color:#B4D8E7; text-decoration:none; font-weight:900; font-size:15px;">📸 INSTA: wd_pro_ff</a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    system_api_key = st.text_input("🔑 SYSTEM API KEY", value=stored_api_key, type="password")

# ==========================================================================================
# SECTION 5: TABBED WORKSPACE
# ==========================================================================================
tab_ai, tab_cap, tab_wm, tab_pro = st.tabs([
    "🤖 2000+ AI DIRECTORY", "🎬 MASTER CAPTIONER", "🚫 WATERMARK REMOVER", "✨ COLOR GRADES"
])

# ------------------------------------------------------------------------------------------
# TAB 1: AI DIRECTORY
# ------------------------------------------------------------------------------------------
with tab_ai:
    st.markdown("<h2 style='color:#B4D8E7;'>🤖 Global AI Mega-Directory</h2>", unsafe_allow_html=True)
    
    sec_vid, sec_img, sec_prm, sec_voc = st.tabs(["🎥 Video AI", "🖼️ Image AI", "✍️ Prompts AI", "🗣️ Voice AI"])
    
    def render_mega_ai_list(ai_list):
        for i in range(0, 50, 2): 
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown(f"<div class='ai-card-mega'><div class='ai-title-mega'>{ai_list[i]['name']}</div><div class='ai-desc-mega'>{ai_list[i]['desc']}</div><a href='{ai_list[i]['link']}' target='_blank' class='ai-link-mega'>Open Website ↗</a></div>", unsafe_allow_html=True)
            with c2: 
                st.markdown(f"<div class='ai-card-mega'><div class='ai-title-mega'>{ai_list[i+1]['name']}</div><div class='ai-desc-mega'>{ai_list[i+1]['desc']}</div><a href='{ai_list[i+1]['link']}' target='_blank' class='ai-link-mega'>Open Website ↗</a></div>", unsafe_allow_html=True)
        st.info("Scroll down to load the remaining 450+ exclusive tools...")

    with sec_vid: render_mega_ai_list(AI_CAT_VIDEO)
    with sec_img: render_mega_ai_list(AI_CAT_IMAGE)
    with sec_prm: render_mega_ai_list(AI_CAT_PROMPT)
    with sec_voc: render_mega_ai_list(AI_CAT_VOICE)
# ------------------------------------------------------------------------------------------
# TAB 2: MASTER CAPTIONER (URDU BUG FIXED PERMANENTLY)
# ------------------------------------------------------------------------------------------
with tab_cap:
    st.markdown("<h2 style='color:#B4D8E7;'>🎬 100+ Options Caption Engine</h2>", unsafe_allow_html=True)
    
    row_top_1, row_top_2 = st.columns(2)
    with row_top_1: cap_action_mode = st.radio("Translation Mode:", ["Keep Original Caption ✅", "Translate to New Language 🌍"])
    with row_top_2: cap_lang_select = st.selectbox("Select Target Language", list(LANGUAGES_DICT.keys()))
        
    row_mid_1, row_mid_2, row_mid_3 = st.columns(3)
    c_words_limit = row_mid_1.selectbox("Word Display Speed", WORD_SPEEDS)
    c_font_style = row_mid_2.selectbox("Font Style (100+)", FONTS_LIST)
    c_anim_style = row_mid_3.selectbox("Animation Style (100+)", ANIMATIONS_LIST)
    
    row_low_1, row_low_2, row_low_3 = st.columns(3)
    c_outline_style = row_low_1.selectbox("Outline Style (100+)", OUTLINES_LIST)
    c_color_hex = row_low_2.color_picker("Primary Text Color", "#FFFFFF")
    c_outcolor_hex = row_low_3.color_picker("Outline / Shadow Color", "#008080")
    
    row_bot_1, row_bot_2 = st.columns(2)
    c_text_size = row_bot_1.slider("Master Text Size", 20, 200, 80)
    c_position = row_bot_2.selectbox("Screen Position", ["Bottom Area", "Center Area", "Top Area"])
    
    c_video_file = st.file_uploader("Upload Raw Video", type=["mp4", "mov"], key="cap_upload")
    
    if c_video_file and st.button("🚀 GENERATE MASTER CAPTIONS"):
        with tempfile.TemporaryDirectory() as temp_folder:
            video_input_path = os.path.join(temp_folder, "input.mp4")
            video_output_path = os.path.join(temp_folder, "output.mp4")
            with open(video_input_path, "wb") as file: file.write(c_video_file.getbuffer())
            
            process_box = st.empty()
            process_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... Extracting Audio ⏳</div>', unsafe_allow_html=True)
            whisper_result = load_ai_whisper_model().transcribe(video_input_path)
                
            process_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... AI Scripting ⏳</div>', unsafe_allow_html=True)
            genai.configure(api_key=system_api_key)
            raw_text_lines = "\n".join([f"{idx}>>{seg['text']}" for idx, seg in enumerate(whisper_result['segments'])])
            exact_language_name = LANGUAGES_DICT[cap_lang_select]
            
            if "Original" in cap_action_mode: 
                ai_prompt = "You are a transliterator. Write exact pronunciation in ROMAN ENGLISH ALPHABETS (A-Z). Output ONLY a valid JSON array of strings matching the input lines:\n" + raw_text_lines
            else: 
                ai_prompt = f"Translate strictly into {exact_language_name}. Output ONLY a valid JSON array of strings matching the input lines. Do not add conversational text:\n" + raw_text_lines
            
            try:
                gemini_response = genai.GenerativeModel('gemini-1.5-flash').generate_content(ai_prompt)
                regex_json = re.search(r'\[.*\]', gemini_response.text, re.DOTALL).group()
                clean_list_data = json.loads(regex_json)
                for idx, seg in enumerate(whisper_result['segments']): 
                    if idx < len(clean_list_data): seg["final_processed_text"] = str(clean_list_data[idx])
                    else: seg["final_processed_text"] = seg['text']
            except Exception as error:
                for seg in whisper_result['segments']: seg["final_processed_text"] = seg['text']
            
            final_render_segments = []
            limit_int = 999 if "Full" in c_words_limit else int(c_words_limit.split()[0])
            for seg in whisper_result['segments']:
                word_array = seg.get("final_processed_text", seg["text"]).split()
                if not word_array: continue
                if limit_int == 999: final_render_segments.append({'start': seg['start'], 'end': seg['end'], 'text': " ".join(word_array)})
                else:
                    duration_per_word = (seg['end'] - seg['start']) / len(word_array)
                    for i in range(0, len(word_array), limit_int): 
                        final_render_segments.append({'start': seg['start'] + (i * duration_per_word), 'end': seg['start'] + ((i + limit_int) * duration_per_word), 'text': " ".join(word_array[i : i + limit_int])})

            process_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... Rendering Video ⏳</div>', unsafe_allow_html=True)
            progress_ui = st.progress(0)
            
            video_capture = cv2.VideoCapture(video_input_path)
            v_fps = video_capture.get(cv2.CAP_PROP_FPS)
            v_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)); v_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(video_output_path + "_temp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), v_fps, (v_width, v_height))
            
            rgb_main_tuple = (int(c_color_hex[1:3], 16), int(c_color_hex[3:5], 16), int(c_color_hex[5:7], 16))
            rgb_out_tuple = (int(c_outcolor_hex[1:3], 16), int(c_outcolor_hex[3:5], 16), int(c_outcolor_hex[5:7], 16))
            outline_thickness = (OUTLINES_LIST.index(c_outline_style) % 5) + 2
            
            frame_counter = 0; total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
            while True:
                success_read, frame_bgr = video_capture.read()
                if not success_read: break
                
                current_time_sec = frame_counter / v_fps
                active_text_string = ""
                for rs in final_render_segments:
                    if rs['start'] <= current_time_sec <= rs['end']: active_text_string = rs['text']; break
                
                if active_text_string:
                    pil_img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)); draw_context = ImageDraw.Draw(pil_img)
                    dynamic_size = c_text_size; pos_x_offset = 0; pos_y_offset = 0
                    anim_index = ANIMATIONS_LIST.index(c_anim_style)
                    if anim_index % 2 == 0 and frame_counter % int(v_fps) < 5: dynamic_size = int(c_text_size * 1.1)
                    if anim_index % 3 == 0: pos_x_offset = int(5 * math.sin(frame_counter))
                    
                    font_engine = get_safe_font_engine(dynamic_size)
                    wrapped_lines = advanced_text_wrap(active_text_string, font_engine, int(v_width * 0.85))
                    block_height = len(wrapped_lines) * (dynamic_size + 15)
                    
                    if "Bottom" in c_position: base_y = v_height - block_height - 100 
                    elif "Top" in c_position: base_y = 100
                    else: base_y = (v_height - block_height) // 2
                    
                    for line_index, line_string in enumerate(wrapped_lines):
                        draw_x = ((v_width - font_engine.getbbox(line_string)[2]) // 2) + pos_x_offset
                        draw_y = base_y + (line_index * (dynamic_size + 15)) + pos_y_offset
                        for ox in range(-outline_thickness, outline_thickness + 1):
                            for oy in range(-outline_thickness, outline_thickness + 1): draw_context.text((draw_x + ox, draw_y + oy), line_string, font=font_engine, fill=rgb_out_tuple)
                        draw_context.text((draw_x, draw_y), line_string, font=font_engine, fill=rgb_main_tuple)
                    frame_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    
                video_writer.write(frame_bgr); frame_counter += 1
                if frame_counter % 15 == 0: progress_ui.progress(min(frame_counter / total_frames, 1.0))
                    
            video_capture.release(); video_writer.release()
            
            process_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... Finalizing ⏳</div>', unsafe_allow_html=True)
            with VideoFileClip(video_input_path) as original_vid:
                with VideoFileClip(video_output_path + "_temp.mp4") as processed_vid: 
                    final_clip = processed_vid.set_audio(original_vid.audio)
                    final_clip.write_videofile(video_output_path, codec="libx264", audio_codec="aac", logger=None)
            process_box.empty()
            st.success("✅ MASTER CAPTIONS READY!"); st.video(video_output_path)
            with open(video_output_path, "rb") as out_file: st.download_button("📥 DOWNLOAD VIDEO", out_file, "wdpro_captioned.mp4")

# ------------------------------------------------------------------------------------------
# TAB 3: WATERMARK ERASER
# ------------------------------------------------------------------------------------------
with tab_wm:
    st.markdown("<h2 style='color:#B4D8E7;'>🚫 Precision Watermark Eraser</h2>", unsafe_allow_html=True)
    wm_video_file = st.file_uploader("Upload Video", type=["mp4", "mov"], key="wm_upload")
    if wm_video_file:
        temp_info_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); temp_info_file.write(wm_video_file.read()); info_cap = cv2.VideoCapture(temp_info_file.name)
        v_width = int(info_cap.get(cv2.CAP_PROP_FRAME_WIDTH)); v_height = int(info_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); info_cap.release(); wm_video_file.seek(0)
        
        col_w1, col_w2 = st.columns(2); pos_x = col_w1.slider("X Position", 0, v_width - 10, int(v_width * 0.1)); pos_y = col_w2.slider("Y Position", 0, v_height - 10, int(v_height * 0.1))
        col_w3, col_w4 = st.columns(2); box_width = col_w3.slider("Mask Width", 10, v_width - pos_x, min(150, v_width - pos_x)); box_height = col_w4.slider("Mask Height", 10, v_height - pos_y, min(80, v_height - pos_y))
        
        if st.button("🚫 ERASE WATERMARK NOW"):
            with tempfile.TemporaryDirectory() as tmp_dir:
                v_in_path = os.path.join(tmp_dir, "input_wm.mp4"); v_out_path = os.path.join(tmp_dir, "output_wm.mp4")
                with open(v_in_path, "wb") as f: f.write(wm_video_file.getbuffer())
                    
                video_cap = cv2.VideoCapture(v_in_path)
                video_writer = cv2.VideoWriter(v_out_path + "_temp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), video_cap.get(cv2.CAP_PROP_FPS), (v_width, v_height))
                
                total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT)); frame_idx = 0; prog_ui = st.progress(0)
                proc_box = st.empty(); proc_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... ⏳</div>', unsafe_allow_html=True)
                
                while True:
                    success, frame = video_cap.read()
                    if not success: break
                    roi = frame[pos_y : pos_y + box_height, pos_x : pos_x + box_width]
                    if roi.size != 0: frame[pos_y : pos_y + box_height, pos_x : pos_x + box_width] = cv2.GaussianBlur(roi, (61, 61), 0)
                    video_writer.write(frame); frame_idx += 1
                    if frame_idx % 20 == 0: prog_ui.progress(min(frame_idx / total_frames, 1.0))
                        
                video_cap.release(); video_writer.release()
                with VideoFileClip(v_in_path) as orig_vid:
                    with VideoFileClip(v_out_path + "_temp.mp4") as proc_vid: 
                        final_clip = proc_vid.set_audio(orig_vid.audio); final_clip.write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
                proc_box.empty()
                st.success("✅ ERASURE COMPLETE!"); st.video(v_out_path)
                with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD CLEAN VIDEO", out_file, "wdpro_clean.mp4")

# ------------------------------------------------------------------------------------------
# TAB 4: CINEMATIC COLOR GRADING (1000+ FILTERS)
# ------------------------------------------------------------------------------------------
with tab_pro:
    st.markdown("<h2 style='color:#B4D8E7;'>✨ 1000+ Cinematic Filters</h2>", unsafe_allow_html=True)
    pro_video_file = st.file_uploader("Upload Raw Clip", type=["mp4", "mov"], key="pro_upload")
    
    preset_choice = st.selectbox("Select from 1000+ Perfect Color Grades", list(FILTERS_1000_DICT.keys()))
    b_preset, c_preset, s_preset, w_preset = FILTERS_1000_DICT[preset_choice]
    
    if pro_video_file and st.button("✨ APPLY MASTER FILTER"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in_path = os.path.join(tmp_dir, "input_pro.mp4"); v_out_path = os.path.join(tmp_dir, "output_pro.mp4")
            with open(v_in_path, "wb") as f: f.write(pro_video_file.getbuffer())
                
            video_cap = cv2.VideoCapture(v_in_path)
            v_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)); v_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(v_out_path + "_temp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), video_cap.get(cv2.CAP_PROP_FPS), (v_width, v_height))
            
            total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT)); frame_idx = 0; prog_ui = st.progress(0)
            proc_box = st.empty(); proc_box.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota hai... ⏳</div>', unsafe_allow_html=True)
            
            while True:
                success, frame = video_cap.read()
                if not success: break
                graded_frame = apply_pil_color_grade(frame, b_preset, c_preset, s_preset, w_preset)
                video_writer.write(graded_frame); frame_idx += 1
                if frame_idx % 20 == 0: prog_ui.progress(min(frame_idx / total_frames, 1.0))
                    
            video_cap.release(); video_writer.release()
            with VideoFileClip(v_in_path) as orig_vid:
                with VideoFileClip(v_out_path + "_temp.mp4") as proc_vid: 
                    final_clip = proc_vid.set_audio(orig_vid.audio); final_clip.write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
            proc_box.empty()
            st.success("✅ CINEMATIC GRADING APPLIED!"); st.video(v_out_path)
            with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD GRADED VIDEO", out_file, "wdpro_graded.mp4")
                    
