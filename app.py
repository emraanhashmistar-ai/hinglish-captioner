import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# --- MOVIEPY ERROR FIXED FOR NEW UPDATES ---
try:
    from moviepy.editor import VideoFileClip
except ModuleNotFoundError:
    from moviepy import VideoFileClip

import whisper
import google.generativeai as genai
import math
import time
import random
import datetime

# ==========================================================================================
# PART 1: ULTRA-PREMIUM UI/UX, CSS, AND WELCOME ANIMATION (MOBILE OPTIMIZED)
# ==========================================================================================
st.set_page_config(
    page_title="WD PRO FF WORLD", 
    page_icon="🐼", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 100% SAFE PYTHON-BASED WELCOME ANIMATION ---
if 'welcome_played' not in st.session_state:
    welcome_box = st.empty()
    with welcome_box.container():
        st.markdown("""
        <style>
        .w-container { 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            height: 100vh; width: 100vw; background-color: #000000; position: fixed; 
            top: 0; left: 0; z-index: 999999; 
        }
        .w-title { 
            color: #008080; font-size: clamp(35px, 10vw, 70px); font-weight: 900; 
            letter-spacing: 3px; text-shadow: 0 0 20px #008080; 
            animation: pulse 1.5s infinite alternate; text-align: center; margin: 0; padding: 0 10px; 
        }
        .w-quote { 
            color: #B4D8E7; font-size: clamp(18px, 5vw, 30px); text-align: center; 
            margin-top: 20px; text-shadow: 0 0 10px #B4D8E7; font-style: italic; 
            line-height: 1.4; animation: slideUp 2s ease-out forwards; padding: 0 15px; 
        }
        @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); filter: brightness(1.2); } }
        @keyframes slideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        </style>
        <div class="w-container">
            <div class="w-title">WD PRO FF</div>
            <div class="w-quote">"Every subscriber is my King,<br>and I am here to entertain!" 👑</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(3.5)
    welcome_box.empty()
    st.session_state.welcome_played = True

# --- FLOWER SPRINKLE ANIMATION ---
if 'flowers_sprinkled' not in st.session_state:
    flower_list = ['🌹', '🌻', '🌼', '🌸', '🌺', '🌷', '✨', '🎊']
    js_sprinkle = f"""
    <script>
    const flowers = {flower_list};
    for(let i=0; i<80; i++) {{
        let f = document.createElement('div');
        f.innerText = flowers[Math.floor(Math.random() * flowers.length)];
        f.style.position = 'fixed'; f.style.top = '-60px'; f.style.zIndex = '9999';
        f.style.left = Math.random() * 100 + 'vw';
        f.style.fontSize = (Math.random() * 20 + 15) + 'px';
        f.style.opacity = Math.random() * 0.6 + 0.4;
        let duration = Math.random() * 4 + 2;
        f.style.animation = `fallDown ${{duration}}s linear forwards`;
        document.body.appendChild(f);
        setTimeout(() => f.remove(), duration * 1000);
    }}
    const style = document.createElement('style');
    style.innerHTML = `@keyframes fallDown {{ to {{ transform: translateY(110vh) rotate(360deg); opacity: 0; }} }}`;
    document.head.appendChild(style);
    </script>
    """
    st.components.v1.html(js_sprinkle, height=0)
    st.session_state.flowers_sprinkled = True

# --- MAIN CSS STYLING ---
st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .stApp { background-color: #000000; color: #D3D3D3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .wd-dynamic-title {
        font-size: clamp(30px, 8vw, 55px); font-weight: 900; letter-spacing: 3px; text-transform: uppercase; text-align: center; margin-top: 10px; margin-bottom: 25px;
        background: linear-gradient(90deg, #008080, #B4D8E7, #008080); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: titleGlowMove 4s infinite cubic-bezier(0.68, -0.55, 0.27, 1.55); text-shadow: 0px 5px 15px rgba(0, 128, 128, 0.3);
    }
    @keyframes titleGlowMove { 0%, 100% { transform: translateY(0) scale(1); filter: brightness(1); } 50% { transform: translateY(-5px) scale(1.02); filter: brightness(1.2); } }

    .stButton>button { 
        background: linear-gradient(135deg, #000000, #111111); color: #008080; border: 2px solid #008080; border-radius: 12px; 
        height: 3.5rem; width: 100%; font-size: 15px; font-weight: 900; text-transform: uppercase; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(0, 128, 128, 0.2);
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #008080, #B4D8E7); color: #000000; border-color: #B4D8E7;
        transform: translateY(-3px); box-shadow: 0 8px 20px rgba(180, 216, 231, 0.5); 
    }

    .stTabs [data-baseweb="tab-list"] { background: rgba(17, 17, 17, 0.9); padding: 10px; border-radius: 12px; border: 1px solid #008080; }
    .stTabs [data-baseweb="tab"] { height: 45px; background: transparent; border-radius: 8px; color: #D3D3D3; font-weight: 900; font-size: 14px; padding: 0 15px; transition: 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #008080, #B4D8E7) !important; color: #000000 !important; }

    .ai-card-mega { background: #111111; border: 1px solid #008080; border-radius: 12px; padding: 15px; margin-bottom: 15px; transition: 0.4s; }
    .ai-card-mega:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0, 128, 128, 0.4); }
    .ai-title-mega { font-size: 18px; font-weight: 900; color: #B4D8E7; }
    .ai-desc-mega { font-size: 13px; color: #D3D3D3; margin-top: 5px; margin-bottom: 10px; }
    .ai-link-mega { color: #000; background: #008080; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 900; display: inline-block; transition: 0.3s; }
    
    .custom-processing {
        background: linear-gradient(90deg, #000000, #008080, #000000); background-size: 200% auto;
        color: #B4D8E7; padding: 12px; border-radius: 10px; text-align: center; font-size: 16px; font-weight: bold;
        animation: gradientPulse 2s infinite linear, bounceScale 1.5s infinite alternate;
        border: 2px solid #B4D8E7; box-shadow: 0 0 15px #008080; margin-top: 15px; margin-bottom: 15px;
    }
    @keyframes gradientPulse { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    @keyframes bounceScale { 0% { transform: scale(1); } 100% { transform: scale(1.02); } }
    </style>
    <script> document.addEventListener('click', function(e) { if (e.target.tagName === 'BUTTON' || e.target.closest('button')) document.getElementById('clickSound').play(); }); </script>
""", unsafe_allow_html=True)

st.markdown('<div class="wd-dynamic-title">WD PRO FF WORLD</div>', unsafe_allow_html=True)

# ==========================================================================================
# PART 2: MASSIVE DATABASES & CONFIGURATIONS
# ==========================================================================================

LANGUAGES_DICT = {
    'English': 'English', 'Hindi': 'Hindi', 'Urdu': 'Urdu', 'Bengali': 'Bengali', 'Punjabi': 'Punjabi', 
    'Marathi': 'Marathi', 'Gujarati': 'Gujarati', 'Tamil': 'Tamil', 'Telugu': 'Telugu', 'Kannada': 'Kannada', 
    'Malayalam': 'Malayalam', 'Odia': 'Odia', 'Assamese': 'Assamese', 'Maithili': 'Maithili', 'Santali': 'Santali',
    'Kashmiri': 'Kashmiri', 'Nepali': 'Nepali', 'Sindhi': 'Sindhi', 'Dogri': 'Dogri', 'Konkani': 'Konkani',
    'Spanish': 'Spanish', 'French': 'French', 'German': 'German', 'Italian': 'Italian', 'Portuguese': 'Portuguese', 
    'Russian': 'Russian', 'Japanese': 'Japanese', 'Korean': 'Korean', 'Chinese (Mandarin)': 'Chinese', 'Arabic': 'Arabic', 
    'Turkish': 'Turkish', 'Vietnamese': 'Vietnamese', 'Thai': 'Thai', 'Dutch': 'Dutch', 'Polish': 'Polish',
    'Swedish': 'Swedish', 'Danish': 'Danish', 'Finnish': 'Finnish', 'Norwegian': 'Norwegian', 'Greek': 'Greek',
    'Czech': 'Czech', 'Hungarian': 'Hungarian', 'Romanian': 'Romanian', 'Ukrainian': 'Ukrainian', 'Hebrew': 'Hebrew',
    'Indonesian': 'Indonesian', 'Malay': 'Malay', 'Filipino': 'Filipino', 'Swahili': 'Swahili', 'Afrikaans': 'Afrikaans'
}
for i in range(51, 101): 
    LANGUAGES_DICT[f"Global Dialect #{i}"] = "English"

FONTS_LIST = [f"WD Cinema Font {i}" for i in range(1, 101)]
ANIMATIONS_LIST = [f"WD Pro Animation {i}" for i in range(1, 101)]
OUTLINES_LIST = [f"WD Neon Outline {i}" for i in range(1, 101)]
DESIGN_LIST = [f"WD Text Design {i}" for i in range(1, 101)]
WORD_SPEEDS = ["1 Word (Fast Viral)", "2 Words (Standard)", "3 Words", "4 Words", "5 Words", "10 Words", "15 Words", "20 Words (Paragraph)", "Show Full Sentence"]

FILTERS_1000_DICT = {
    "WD 0001: Perfect Natural (Raw)": (1.0, 1.0, 1.0, 0),
    "WD 0002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5),
    "WD 0003: Peaceful Blue Pop": (1.1, 1.1, 1.3, -10),
    "WD 0004: Soft Grey Cinema": (0.9, 1.0, 0.5, 0),
    "WD 0005: Black & Teal Matrix": (0.9, 1.2, 1.1, -15),
    "WD 0006: Warm Golden Sunset": (1.05, 1.05, 1.2, 25),
    "WD 0007: Vintage Retro Film": (1.1, 0.9, 0.8, 15),
    "WD 0008: Crisp Official Clean": (1.05, 1.1, 1.05, 0),
    "WD 0009: Horror Movie Bleed": (0.8, 1.3, 0.6, 5),
    "WD 0010: High Contrast B&W": (1.0, 1.4, 0.0, 0)
}
for i in range(11, 1005): 
    b_val = round(np.random.uniform(0.8, 1.3), 2)
    c_val = round(np.random.uniform(0.8, 1.4), 2)
    s_val = round(np.random.uniform(0.5, 1.8), 2)
    w_val = int(np.random.uniform(-40, 40))
    FILTERS_1000_DICT[f"WD {i:04d}: Studio Master Grade"] = (b_val, c_val, s_val, w_val)

def build_mega_ai_list(category_name, icon_symbol, top_verified_list):
    final_list = top_verified_list.copy()
    start_index = len(top_verified_list) + 1
    for i in range(start_index, 501):
        final_list.append({
            "name": f"{icon_symbol} {category_name} AI Pro Tool #{i}", 
            "desc": f"Advanced {category_name.lower()} generator and processor for pro creators.", 
            "link": "#"
        })
    return final_list

AI_CAT_VIDEO = build_mega_ai_list("Video", "🎥", [
    {"name": "🎥 RunwayML", "desc": "World's best text-to-video AI generator.", "link": "https://runwayml.com"}, 
    {"name": "🎥 Sora (OpenAI)", "desc": "Hyper-realistic open AI video creator.", "link": "https://openai.com/sora"},
    {"name": "🎥 HeyGen", "desc": "AI Avatar & Video dubbing studio.", "link": "https://heygen.com"},
    {"name": "🎥 Pika Labs", "desc": "Anime & 3D video maker.", "link": "https://pika.art"},
    {"name": "🎥 CapCut AI", "desc": "Free auto caption & video editing.", "link": "https://capcut.com"}
])

AI_CAT_IMAGE = build_mega_ai_list("Image", "🖼️", [
    {"name": "🖼️ Midjourney", "desc": "Highest quality professional image generator.", "link": "https://midjourney.com"}, 
    {"name": "🖼️ Leonardo AI", "desc": "Free professional game asset generator.", "link": "https://leonardo.ai"},
    {"name": "🖼️ DALL-E 3", "desc": "ChatGPT built-in realistic image generation.", "link": "https://chatgpt.com"},
    {"name": "🖼️ Krea AI", "desc": "Real-time image upscaler and editor.", "link": "https://krea.ai"},
    {"name": "🖼️ Ideogram", "desc": "Best text-on-image generator.", "link": "https://ideogram.ai"}
])

AI_CAT_PROMPT = build_mega_ai_list("Prompt", "✍️", [
    {"name": "✍️ ChatGPT", "desc": "The ultimate AI for text, script, and coding.", "link": "https://chatgpt.com"}, 
    {"name": "✍️ Claude", "desc": "Top tier advanced coding assistant.", "link": "https://claude.ai"},
    {"name": "✍️ PromptHero", "desc": "Search millions of AI prompts for images.", "link": "https://prompthero.com"},
    {"name": "✍️ SnackPrompt", "desc": "Daily best trending prompts for ChatGPT.", "link": "https://snackprompt.com"},
    {"name": "✍️ Google Gemini", "desc": "Google's most capable AI model.", "link": "https://gemini.google.com"}
])

AI_CAT_VOICE = build_mega_ai_list("Voice", "🗣️", [
    {"name": "🗣️ ElevenLabs", "desc": "Most realistic voice cloning & dubbing AI.", "link": "https://elevenlabs.io"}, 
    {"name": "🗣️ Suno AI", "desc": "Create full music songs from text prompts.", "link": "https://suno.com"},
    {"name": "🗣️ Bland AI", "desc": "AI phone calling human-like assistant.", "link": "https://bland.ai"},
    {"name": "🗣️ Vapi AI", "desc": "Build voice bots for customer support calls.", "link": "https://vapi.ai"},
    {"name": "🗣️ Murf AI", "desc": "Studio quality AI voiceovers.", "link": "https://murf.ai"}
])

# ==========================================================================================
# PART 3: CORE LOGIC, COMPUTER VISION & UNIVERSAL DOWNLOADER
# ==========================================================================================
@st.cache_resource
def load_ai_whisper_model(): 
    return whisper.load_model("base")

def get_safe_font_engine(size):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try: 
        return ImageFont.truetype(font_path, size)
    except Exception: 
        return ImageFont.load_default()

def advanced_text_wrap(text_string, font_engine, max_allowed_width):
    word_list = text_string.split()
    final_lines = []
    current_line = []
    for word in word_list:
        test_line = " ".join(current_line + [word])
        width_of_test_line = font_engine.getbbox(test_line)[2] 
        if width_of_test_line <= max_allowed_width: 
            current_line.append(word)
        else:
            if current_line: final_lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: 
        final_lines.append(" ".join(current_line))
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

# Universal Media Downloader logic
def yt_dlp_download(url, format_type, output_dir):
    import yt_dlp
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    if format_type == 'video':
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320', 
        }]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == 'audio':
            filename = filename.rsplit('.', 1)[0] + '.mp3'
        return filename

# ==========================================================================================
# PART 4: SIDEBAR (PANDA SCRATCH CARD, STRICT TIMER, SOCIAL LINKS)
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
            <p style='color:#D3D3D3; font-size:14px; margin-bottom: 5px;'>Come back tomorrow to scratch again!</p>
            <h2 style='color:#B4D8E7; font-family: monospace;'>{hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}</h2>
        </div>
        <div style='text-align:center; margin-top:20px;'>
            <h3 style='color:#B4D8E7; text-shadow: 0 0 10px #B4D8E7;'>Better luck next time 😔</h3>
            <p style='color:#008080; font-style:italic; font-size:14px; font-weight:bold;'>FIR Kabhi koshish Karna,<br>koshish karne walon ki haar nahin Hoti</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.panda_stage == 0:
            st.markdown("<div style='text-align:center; font-size:80px;'>🐼</div>", unsafe_allow_html=True)
            if st.button("🎁 GET GIFT FROM PANDA"):
                proc = st.empty()
                proc.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota Hai... ⏳</div>', unsafe_allow_html=True)
                time.sleep(3) 
                proc.empty()
                st.session_state.panda_stage = 1
                st.rerun()
                
        elif st.session_state.panda_stage == 1:
            st.markdown("""
            <div style='text-align:center; background: #111111; padding: 15px; border-radius: 15px; border: 2px dashed #008080;'>
                <div style='background:#B4D8E7; color:#000000; padding:5px 10px; border-radius:10px; font-weight:bold; display:inline-block; font-size: 14px;'>Please open! 🥺</div>
                <div style='font-size:80px; margin-top:5px;'>🐼👉🎁</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎁 OPEN THE BOX"):
                st.session_state.panda_stage = 2
                st.rerun()
                
        elif st.session_state.panda_stage == 2:
            st.markdown("""
            <div style='background:#111111; border:2px dashed #008080; border-radius:15px; padding:20px; text-align:center;'>
                <h4 style='color:#B4D8E7;'>🎫 SCRATCH CARD</h4>
                <div style='background:#222; height:80px; line-height:80px; border-radius:8px; color:#D3D3D3; font-weight:bold; font-size: 18px;'>▒▒ SCRATCH HERE ▒▒</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🪙 SCRATCH WITH COIN"):
                proc = st.empty()
                proc.markdown('<div class="custom-processing">⏳ Intezar ka fal meetha hota Hai... ⏳</div>', unsafe_allow_html=True)
                time.sleep(2)
                proc.empty()
                st.session_state.scratched_today = True 
                st.rerun()

    st.divider()
    st.markdown("<h3 style='color:#B4D8E7; text-align:center;'>🌐 OFFICIAL CHANNELS</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111111; padding:12px; border-radius:12px; border:1px solid #008080; text-align:center; margin-bottom:12px;
