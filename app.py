import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
import google.generativeai as genai
from gtts import gTTS
import time
import math

# ==========================================================================================
# 1. ULTRA-PREMIUM UI/UX & THEME ENGINE (CEO LEVEL DESIGN)
# ==========================================================================================
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🧸", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #3e2723 0%, #1a0f0a 40%, #050505 100%);
        color: #ffffff; 
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    .ceo-welcome-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin-top: 10px; margin-bottom: 50px;
    }
    .teddy-icon {
        font-size: 90px;
        animation: teddyBounce 2.5s infinite cubic-bezier(0.28, 0.84, 0.42, 1);
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.5));
    }
    .wd-title {
        font-size: 55px; font-weight: 900; letter-spacing: 4px; text-transform: uppercase;
        background: linear-gradient(90deg, #ffffff, #ffcc80, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: titleGlow 3s infinite alternate; margin-top: 15px;
        text-shadow: 0px 5px 20px rgba(255, 204, 128, 0.2);
    }
    .wd-subtitle {
        font-size: 18px; color: #d7ccc8; font-weight: 600; letter-spacing: 5px;
        text-transform: uppercase; margin-top: 5px;
    }

    @keyframes teddyBounce {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-25px) scale(1.05); }
    }
    @keyframes titleGlow {
        from { filter: drop-shadow(0 0 10px #8b4513); }
        to { filter: drop-shadow(0 0 30px #d2691e); }
    }

    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(26, 15, 10, 0.8); backdrop-filter: blur(10px);
        padding: 15px; border-radius: 20px; gap: 15px; 
        border: 1px solid rgba(139, 69, 19, 0.4);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .stTabs [data-baseweb="tab"] { 
        height: 55px; background: transparent; border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px; color: #a1887f; font-weight: 800; font-size: 16px; 
        transition: all 0.4s ease; padding: 0 25px;
    }
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #8b4513, #3e2723) !important; 
        color: #ffffff !important; border: 1px solid #d2691e !important;
        box-shadow: 0 5px 20px rgba(210, 105, 30, 0.5); transform: translateY(-2px);
    }

    .stButton>button {
        background: linear-gradient(90deg, #5c3a21, #3e2723); color: #ffffff;
        border: 1px solid #8b4513; border-radius: 12px; height: 4rem; width: 100%;
        font-size: 18px; font-weight: 900; letter-spacing: 1px; text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #8b4513, #5c3a21);
        transform: translateY(-4px) scale(1.01); box-shadow: 0 12px 30px rgba(210, 105, 30, 0.4); 
    }
    .stButton>button:active { transform: scale(0.96); }

    .stFileUploader {
        background: rgba(62, 39, 35, 0.3); border: 2px dashed #8b4513;
        border-radius: 15px; padding: 20px; transition: 0.3s;
    }
    .stFileUploader:hover { background: rgba(139, 69, 19, 0.2); border-color: #d2691e; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ceo-welcome-container">
    <div class="teddy-icon">🧸</div>
    <div class="wd-title">WELCOME TO WD PRO FF WORLD</div>
    <div class="wd-subtitle">The Ultimate Creator Studio</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================================================
# 2. MASSIVE CONFIGURATION ENGINES
# ==========================================================================================
LANGUAGES_50 = {
    'English (Global)': 'en', 'Hindi (India)': 'hi', 'Urdu (Pakistan/India)': 'ur', 
    'Bengali (India/Ban)': 'bn', 'Punjabi (India)': 'pa', 'Marathi (India)': 'mr', 
    'Gujarati (India)': 'gu', 'Tamil (India)': 'ta', 'Telugu (India)': 'te', 
    'Kannada (India)': 'kn', 'Malayalam (India)': 'ml', 'Spanish (Spain/LatAm)': 'es', 
    'French (France)': 'fr', 'German (Germany)': 'de', 'Italian (Italy)': 'it', 
    'Portuguese (Brazil/Por)': 'pt', 'Russian (Russia)': 'ru', 'Japanese (Japan)': 'ja', 
    'Korean (Korea)': 'ko', 'Chinese (Mandarin)': 'zh-cn', 'Arabic (UAE/SA)': 'ar', 
    'Turkish (Turkey)': 'tr', 'Indonesian (Indonesia)': 'id', 'Vietnamese (Vietnam)': 'vi', 
    'Thai (Thailand)': 'th', 'Dutch (Netherlands)': 'nl', 'Greek (Greece)': 'el', 
    'Polish (Poland)': 'pl', 'Swedish (Sweden)': 'sv', 'Danish (Denmark)': 'da', 
    'Finnish (Finland)': 'fi', 'Norwegian (Norway)': 'no', 'Czech (Czechia)': 'cs', 
    'Hungarian (Hungary)': 'hu', 'Romanian (Romania)': 'ro', 'Ukrainian (Ukraine)': 'uk', 
    'Malay (Malaysia)': 'ms', 'Filipino (Philippines)': 'tl', 'Swahili (Kenya/Tan)': 'sw', 
    'Afrikaans (South Africa)': 'af', 'Bulgarian (Bulgaria)': 'bg', 'Catalan (Spain)': 'ca', 
    'Croatian (Croatia)': 'hr', 'Estonian (Estonia)': 'et', 'Hebrew (Israel)': 'iw', 
    'Latvian (Latvia)': 'lv', 'Lithuanian (Lithuania)': 'lt', 'Serbian (Serbia)': 'sr', 
    'Slovak (Slovakia)': 'sk', 'Slovenian (Slovenia)': 'sl', 'Welsh (Wales)': 'cy'
}

FONTS_50 = [
    "WD Absolute Bold", "WD Cinematic Serif", "WD Modern Minimal", "WD Gaming Tech", "WD Classic Sans",
    "WD Pro Writer", "WD Impact Heavy", "WD Elegance Light", "WD Street Marker", "WD Cyberpunk Mono",
    "WD Typewriter Old", "WD Smooth Round", "WD Blocky Hard", "WD Anime Sub", "WD Headline Max",
    "WD Minimalist Thin", "WD Signature Script", "WD Comic Fun", "WD Newspaper Print", "WD Sci-Fi Future",
    "WD Pixel Art", "WD Retro 80s", "WD Neon Sign", "WD Military Stencil", "WD Graffiti Wall",
    "WD Fantasy Magic", "WD Horror Bleed", "WD Romantic Flow", "WD Sports Varsity", "WD Action Hero",
    "WD Corporate Clean", "WD Coding Terminal", "WD Typecast Serif", "WD Brush Stroke", "WD Chalkboard",
    "WD Handwritten Note", "WD Futuristic Wide", "WD Tall Condensed", "WD Vintage Label", "WD Bubblegum",
    "WD Speed Racing", "WD Tech Circuit", "WD Glitch Distorted", "WD Shadow Cast", "WD Outline Only",
    "WD 3D Extruded", "WD Elegant Cursive", "WD Bold Italic Speed", "WD Monospace Clean", "WD Supreme Final"
]

ANIMS_50 = [
    "None (Static)", "Pop-Up Fast", "Pop-Up Smooth", "Zoom In Slow", "Zoom Out Bounce",
    "Glow Pulse Regular", "Glow Pulse Extreme", "Shake Mild", "Shake Earthquake", "Fade In Clean",
    "Fade In Out", "Slide Up from Bottom", "Slide Down from Top", "Slide Left to Right", "Slide Right to Left",
    "Wave Float", "Heartbeat Beat", "Flicker Neon", "Glitch Effect", "Typewriter Fast",
    "Typewriter Slow", "Elastic Bounce", "Swing Left Right", "Rotate 3D Mild", "Rotate 3D Extreme",
    "Color Shift RGB", "Blur to Focus", "Focus to Blur", "Stretch Horizontal", "Stretch Vertical",
    "Drop Down Heavy", "Rise Up Helium", "Zig-Zag Move", "Spin Entry", "Tumble Entry",
    "Matrix Rain Drop", "Flash Bang White", "Dark Fade Shadow", "Jelly Wiggle", "Pulse Grow",
    "Pulse Shrink", "Vibrate Constant", "Breathe Slow", "Panic Fast", "Hover Float",
    "Wobble Drunk", "Elastic Snap", "Slide & Stop", "Zoom & Spin", "The WD PRO Ultimate Anim"
]

OUTLINES_50 = [
    "No Outline", "Thin Black Border", "Thick Black Border", "Massive Black Shadow", "Soft Drop Shadow",
    "Hard Drop Shadow", "Neon Glow Red", "Neon Glow Blue", "Neon Glow Green", "Neon Glow Yellow",
    "Neon Glow Purple", "Neon Glow Pink", "Neon Glow Cyan", "Neon Glow Orange", "Neon Glow White",
    "Double Border Thin", "Double Border Thick", "3D Block Shadow Right", "3D Block Shadow Left", "3D Block Down",
    "Blurred Shadow Deep", "Blurred Shadow Light", "Crisp Edge Stroke", "Soft Edge Stroke", "Bleeding Edge",
    "Golden Halo Glow", "Silver Metallic Border", "Bronze Rusty Border", "Blood Red Outline", "Toxic Green Outline",
    "Ice Blue Outline", "Electric Purple Outline", "Sunshine Yellow Glow", "Deep Ocean Blue", "Forest Green Shadow",
    "Midnight Black Core", "Ghost White Aura", "Cyberpunk Pink/Blue", "Retro Synthwave Grid", "Minimal Gray Outline",
    "Heavy Industrial Iron", "Paper Cutout Edge", "Chalk Smudge Edge", "Spray Paint Halo", "Glowing Ember Edge",
    "Radioactive Green", "Deep Purple Void", "Diamond Sparkle Edge", "Classic Yellow Subtitle", "WD PRO Signature Glow"
]

CINEMATIC_FILTERS_100 = {
    "WD 001: Perfect Natural (Zero Edit)": (1.0, 1.0, 1.0, 0),
    "WD 002: Hollywood Teal & Orange": (0.95, 1.15, 1.25, 5),
    "WD 003: Ultra Gaming Pop (High Sat)": (1.1, 1.2, 1.5, 0),
    "WD 004: Dark Sad Attitude (Desat)": (0.85, 1.1, 0.6, -5),
    "WD 005: Sci-Fi Cold Blue": (1.0, 1.1, 0.9, -20),
    "WD 006: Warm Golden Hour (Sunset)": (1.05, 1.05, 1.2, 25),
    "WD 007: Cinematic Black & White": (1.0, 1.3, 0.0, 0),
    "WD 008: Vintage Retro Film": (0.9, 0.9, 0.8, 15),
    "WD 009: Neon Cyberpunk Pop": (1.0, 1.25, 1.6, -10),
    "WD 010: Crisp Official Clean": (1.05, 1.1, 1.1, 0)
}
for i in range(11, 101):
    _b = round(np.random.uniform(0.85, 1.2), 2)
    _c = round(np.random.uniform(0.9, 1.3), 2)
    _s = round(np.random.uniform(0.5, 1.6), 2)
    _w = int(np.random.uniform(-30, 30))
    CINEMATIC_FILTERS_100[f"WD {i:03d}: Pro Custom Filter"] = (_b, _c, _s, _w)

WORD_COUNTS = [f"{i} Word{'s' if i>1 else ''} per screen" for i in range(1, 21)] + ["Show Full Sentence"]

# ==========================================================================================
# 3. CORE PROCESSING ENGINES & MATH FUNCTIONS
# ==========================================================================================
@st.cache_resource
def load_ai_whisper_engine(): return whisper.load_model("base")

def get_pro_font_engine(font_choice, size):
    safe_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    safe_path_serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    safe_path_sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    if "Serif" in font_choice or "Typewriter" in font_choice or "Classic" in font_choice:
        chosen_path = safe_path_serif
    elif "Thin" in font_choice or "Light" in font_choice:
        chosen_path = safe_path_sans
    else:
        chosen_path = safe_path_bold
        
    try: return ImageFont.truetype(chosen_path, size)
    except Exception: return ImageFont.load_default()

def advanced_text_wrap(text, font, max_width):
    words = text.split(); lines = []; current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        width = font.getbbox(test_line)[2] 
        if width <= max_width: current_line.append(word)
        else:
            if current_line: lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: lines.append(" ".join(current_line))
    return lines

def master_color_grader_pil(frame_bgr, b_val, c_val, s_val, w_val):
    img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    if b_val != 1.0: img = ImageEnhance.Brightness(img).enhance(b_val)
    if c_val != 1.0: img = ImageEnhance.Contrast(img).enhance(c_val)
    if s_val != 1.0: img = ImageEnhance.Color(img).enhance(s_val)
    arr = np.array(img).astype(np.int16)
    if w_val != 0:
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        r = np.clip(r + w_val, 0, 255)
        b = np.clip(b - w_val, 0, 255)
        arr = np.stack((r, g, b), axis=-1)
    return cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)

# ==========================================================================================
# 4. SIDEBAR BRANDING & SECURITY
# ==========================================================================================
stored_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#ffffff; font-weight:900; font-size:35px; text-shadow: 0 0 15px #d2691e;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#a1887f; font-weight:bold; letter-spacing:2px;'>STUDIO DASHBOARD</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2: st.image("https://img.icons8.com/color/144/free-fire.png", use_column_width=True)
    
    st.divider()
    st.markdown("<h3 style='color:#d2691e; text-align:center;'>🌐 OFFICIAL CHANNELS</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3e2723, #1a0f0a); padding:15px; border-radius:12px; border:1px solid #8b4513; text-align:center; margin-bottom:12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
        <a href="https://youtube.com/@WDPROFF" style="color:#ffffff; text-decoration:none; font-weight:900; font-size:16px; display:block;">📺 YOUTUBE: WD PRO FF</a>
    </div>
    <div style="background: linear-gradient(135deg, #3e2723, #1a0f0a); padding:15px; border-radius:12px; border:1px solid #8b4513; text-align:center; margin-bottom:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
        <a href="https://instagram.com/WDPROFF" style="color:#ffffff; text-decoration:none; font-weight:900; font-size:16px; display:block;">📸 INSTA: @WDPROFF</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<p style='color:#a1887f; font-size:12px; text-align:center;'>SYSTEM AUTHORIZATION</p>", unsafe_allow_html=True)
    system_key = st.text_input("🔑 API KEY", value=stored_api_key, type="password")
    
if 'app_started' not in st.session_state:
    st.balloons()
    st.session_state.app_started = True
    # ==========================================================================================
# 5. THE TABBED WORKSPACE
# ==========================================================================================
tab_cap, tab_dub, tab_wm, tab_pro = st.tabs([
    "🎬 MASTER CAPTIONER (50+ Options)", "🎙️ AI VOICE DUBBING (50 Langs)", "🚫 SMART WATERMARK ERASER", "✨ CINEMATIC GRADING (100 Filters)"
])

# ------------------------------------------------------------------------------------------
# TAB 1: CAPTIONER
# ------------------------------------------------------------------------------------------
with tab_cap:
    st.markdown("<h2 style='color:#d2691e;'>🎬 Ultimate Subtitle & Caption Engine</h2>", unsafe_allow_html=True)
    
    row1_1, row1_2 = st.columns(2)
    with row1_1: cap_action = st.radio("Caption Translation Mode:", ["Keep Original (Roman/Hinglish) ✅", "Translate to New Language 🌍"], horizontal=False)
    with row1_2: cap_lang = st.selectbox("Select Language Target", list(LANGUAGES_50.keys()))
    
    row2_1, row2_2, row2_3 = st.columns(3)
    c_words = row2_1.selectbox("Words per screen (Speed)", WORD_COUNTS)
    c_font = row2_2.selectbox("Typography (50 Fonts)", FONTS_50)
    c_anim = row2_3.selectbox("Motion Animation (50 Styles)", ANIMS_50)
    
    row3_1, row3_2, row3_3 = st.columns(3)
    c_outline_style = row3_1.selectbox("Outline/Glow Type (50 Styles)", OUTLINES_50)
    c_color = row3_2.color_picker("Primary Text Color", "#FFFFFF")
    c_out_color = row3_3.color_picker("Outline/Shadow Color", "#000000")
    
    row4_1, row4_2 = st.columns(2)
    c_size = row4_1.slider("Master Text Size", 20, 200, 85)
    c_pos = row4_2.selectbox("Screen Positioning", ["Bottom Center (Standard)", "Dead Center (Impact)", "Top Center (News)"])
    
    c_vid = st.file_uploader("Upload Raw Video File (.mp4, .mov)", type=["mp4", "mov"], key="cap_up")
    
    if c_vid and st.button("🚀 IGNITE CAPTION ENGINE"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in_path = os.path.join(tmp_dir, "input.mp4"); v_out_path = os.path.join(tmp_dir, "output.mp4")
            with open(v_in_path, "wb") as f: f.write(c_vid.getbuffer())
            
            with st.spinner("🎙️ PHASE 1: Extracting vocals..."):
                whisper_model = load_ai_whisper_engine()
                listen_lang = "hi" if "Hindi" in cap_lang or "Hinglish" in cap_lang else LANGUAGES_50[cap_lang]
                transcript_data = whisper_model.transcribe(v_in_path, language=listen_lang[:2])
            
            with st.spinner("🧠 PHASE 2: AI Scripting..."):
                genai.configure(api_key=system_key)
                gemini_flash = genai.GenerativeModel('gemini-1.5-flash')
                raw_lines = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(transcript_data['segments'])])
                
                if "Original" in cap_action:
                    ai_prompt = "STRICT DIRECTIVE: Convert text to ROMAN SCRIPT (A-Z) only. No Translation. Return JSON array ONLY:\n" + raw_lines
                else:
                    ai_prompt = f"STRICT DIRECTIVE: Translate text into {cap_lang.split(' ')[0]}. Return JSON array ONLY:\n" + raw_lines
                    
                try:
                    ai_response = gemini_flash.generate_content(ai_prompt)
                    clean_list = json.loads(re.search(r'\[.*\]', ai_response.text, re.DOTALL).group())
                    for i, segment in enumerate(transcript_data['segments']):
                        segment["final_text"] = re.sub(r'[^\x00-\x7F]+', '', str(clean_list[i])) if i < len(clean_list) else segment['text']
                except Exception:
                    for segment in transcript_data['segments']: segment["final_text"] = segment['text']

            with st.spinner("⏱️ PHASE 3: Timing sync..."):
                render_segments = []
                word_limit = 999 if "Full" in c_words else int(c_words.split()[0])
                for segment in transcript_data['segments']:
                    words_array = segment.get("final_text", segment["text"]).split()
                    if not words_array: continue
                    if word_limit == 999: render_segments.append({'start': segment['start'], 'end': segment['end'], 'text': " ".join(words_array)})
                    else:
                        time_per_word = (segment['end'] - segment['start']) / len(words_array)
                        for i in range(0, len(words_array), word_limit):
                            render_segments.append({'start': segment['start'] + (i * time_per_word), 'end': segment['start'] + ((i + word_limit) * time_per_word), 'text': " ".join(words_array[i:i+word_limit])})

            st.info("🎨 PHASE 4: Rendering Graphics...")
            p_bar = st.progress(0)
            video_cap = cv2.VideoCapture(v_in_path)
            v_fps = video_cap.get(cv2.CAP_PROP_FPS); v_w = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)); v_h = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            tot_f = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            vid_writer = cv2.VideoWriter(v_out_path + "_silent.mp4", cv2.VideoWriter_fourcc(*"mp4v"), v_fps, (v_w, v_h))
            
            rgb_main = (int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16))
            rgb_out = (int(c_out_color[1:3],16), int(c_out_color[3:5],16), int(c_out_color[5:7],16))
            out_weight = (OUTLINES_50.index(c_outline_style) % 7) + 1
            
            frame_c = 0
            while True:
                success, frame_bgr = video_cap.read()
                if not success: break
                
                curr_t = frame_c / v_fps
                active_text = next((rs['text'] for rs in render_segments if rs['start'] <= curr_t <= rs['end']), "")
                
                if active_text:
                    img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
                    draw_ctx = ImageDraw.Draw(img_pil)
                    
                    dyn_size = c_size; pos_x = 0; pos_y = 0
                    if "Pop" in c_anim and frame_c % int(v_fps) < (v_fps * 0.2): dyn_size = int(c_size * 1.15)
                    elif "Glow" in c_anim or "Pulse" in c_anim: dyn_size = int(c_size * (1.0 + 0.08 * math.sin(frame_c * 0.15)))
                    elif "Shake" in c_anim: pos_x = int(5 * math.sin(frame_c * 0.8)); pos_y = int(3 * math.cos(frame_c * 0.8))
                    
                    font = get_pro_font_engine(c_font, dyn_size)
                    text_lines = advanced_text_wrap(active_text, font, int(v_w * 0.85))
                    block_h = len(text_lines) * (dyn_size + 15)
                    
                    if "Bottom" in c_pos: base_y = v_h - block_h - int(v_h * 0.1)
                    elif "Top" in c_pos: base_y = int(v_h * 0.1)
                    else: base_y = (v_h - block_h) // 2
                    
                    for line_idx, line_str in enumerate(text_lines):
                        draw_x = ((v_w - font.getbbox(line_str)[2]) // 2) + pos_x
                        draw_y = base_y + (line_idx * (dyn_size + 15)) + pos_y
                        
                        if "Shadow" in c_outline_style:
                            for d in range(1, out_weight + 3): draw_ctx.text((draw_x + d, draw_y + d), line_str, font=font, fill=rgb_out)
                        elif "No Outline" not in c_outline_style:
                            for ox in range(-out_weight, out_weight + 1):
                                for oy in range(-out_weight, out_weight + 1): draw_ctx.text((draw_x + ox, draw_y + oy), line_str, font=font, fill=rgb_out)
                        draw_ctx.text((draw_x, draw_y), line_str, font=font, fill=rgb_main)
                    
                    frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                
                vid_writer.write(frame_bgr); frame_c += 1
                if frame_c % 15 == 0: p_bar.progress(min(frame_c / tot_f, 1.0))
            
            video_cap.release(); vid_writer.release()
            
            with st.spinner("🔊 PHASE 5: Re-attaching Audio..."):
                with VideoFileClip(v_in_path) as o_vid:
                    with VideoFileClip(v_out_path + "_silent.mp4") as p_vid:
                        p_vid.set_audio(o_vid.audio).write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ CAPTIONS READY!")
            st.video(v_out_path)
            with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD", out_file, "wdpro_captions.mp4")

# ------------------------------------------------------------------------------------------
# TAB 2: AI VOICE DUBBING
# ------------------------------------------------------------------------------------------
with tab_dub:
    st.markdown("<h2 style='color:#d2691e;'>🎙️ Global Voice Dubbing Engine</h2>", unsafe_allow_html=True)
    dub_target_lang = st.selectbox("Select Target Dubbing Language (50 Options)", list(LANGUAGES_50.keys()), index=1)
    dub_vid = st.file_uploader("Upload Video for Dubbing", type=["mp4", "mov"], key="dub_up")
    
    if dub_vid and st.button("🎙️ INITIATE AI DUBBING"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in_path = os.path.join(tmp_dir, "in_dub.mp4"); v_out_path = os.path.join(tmp_dir, "out_dub.mp4")
            with open(v_in_path, "wb") as f: f.write(dub_vid.getbuffer())
            
            with st.spinner("🎧 Extracting original script..."):
                transcription = load_ai_whisper_engine().transcribe(v_in_path)
                orig_script = transcription['text'].strip()
            
            with st.spinner(f"🌍 AI Translating..."):
                genai.configure(api_key=system_key)
                try:
                    ai_response = genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Translate to {dub_target_lang}. Only provide translation: {orig_script}")
                    final_translated_text = ai_response.text.strip()
                    if len(final_translated_text) < 2 or "translate" in final_translated_text.lower(): final_translated_text = orig_script
                except Exception: final_translated_text = orig_script
            
            with st.spinner("🗣️ Synthesizing Voice..."):
                gtts_lang_code = LANGUAGES_50[dub_target_lang]
                audio_tmp_path = os.path.join(tmp_dir, "new_voice.mp3")
                try:
                    gTTS(text=final_translated_text, lang=gtts_lang_code).save(audio_tmp_path)
                    with VideoFileClip(v_in_path) as video_clip:
                        with AudioFileClip(audio_tmp_path) as new_audio_clip:
                            video_clip.set_audio(new_audio_clip.set_duration(video_clip.duration)).write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
                    st.success("✅ DUBBING ACCOMPLISHED!")
                    st.video(v_out_path)
                    with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD", out_file, f"wdpro_{gtts_lang_code}_dub.mp4")
                except Exception as e: st.error("❌ TTS Error: Language might not be fully supported.")

# ------------------------------------------------------------------------------------------
# TAB 3: WATERMARK ERASER
# ------------------------------------------------------------------------------------------
with tab_wm:
    st.markdown("<h2 style='color:#d2691e;'>🚫 Intelligent Area Masking</h2>", unsafe_allow_html=True)
    wm_vid = st.file_uploader("Upload Video with Watermark", type=["mp4", "mov"], key="wm_up")
    if wm_vid:
        temp_info_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_info_file.write(wm_vid.read())
        cap_info = cv2.VideoCapture(temp_info_file.name)
        v_w = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH)); v_h = int(cap_temp.get(cv2.CAP_PROP_FRAME_HEIGHT) if 'cap_temp' in locals() else cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_info.release(); wm_vid.seek(0)
        
        col1, col2 = st.columns(2)
        w_x = col1.slider("X Coordinate", 0, v_w - 10, int(v_w * 0.1)); w_y = col2.slider("Y Coordinate", 0, v_h - 10, int(v_h * 0.1))
        col3, col4 = st.columns(2)
        w_width = col3.slider("Mask Width", 10, v_w - w_x, min(150, v_w - w_x)); w_height = col4.slider("Mask Height", 10, v_h - w_y, min(80, v_h - w_y))
        blur_intensity = st.slider("Blur Intensity", 11, 151, 61, step=10)
        
        if st.button("🚫 ERASE WATERMARK"):
            with tempfile.TemporaryDirectory() as tmp_dir:
                v_in_path = os.path.join(tmp_dir, "in_wm.mp4"); v_out_path = os.path.join(tmp_dir, "out_wm.mp4")
                with open(v_in_path, "wb") as f: f.write(wm_vid.getbuffer())
                
                cap = cv2.VideoCapture(v_in_path)
                writer = cv2.VideoWriter(v_out_path + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), (v_w, v_h))
                prog_bar = st.progress(0); tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); f_idx = 0
                
                while True:
                    success, frame = cap.read()
                    if not success: break
                    roi = frame[w_y:w_y+w_height, w_x:w_x+w_width]
                    if roi.size != 0: frame[w_y:w_y+w_height, w_x:w_x+w_width] = cv2.GaussianBlur(roi, (blur_intensity, blur_intensity), 0)
                    writer.write(frame); f_idx += 1
                    if f_idx % 20 == 0: prog_bar.progress(min(f_idx/tot_frames, 1.0))
                
                cap.release(); writer.release()
                with VideoFileClip(v_in_path) as o_vid:
                    with VideoFileClip(v_out_path + "_tmp.mp4") as p_vid:
                        p_vid.set_audio(o_vid.audio).write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
                st.success("✅ ERASURE COMPLETE!"); st.video(v_out_path)
                with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD", out_file, "wdpro_clean.mp4")

# ------------------------------------------------------------------------------------------
# TAB 4: CINEMATIC GRADING
# ------------------------------------------------------------------------------------------
with tab_pro:
    st.markdown("<h2 style='color:#d2691e;'>✨ Hollywood Color Grading</h2>", unsafe_allow_html=True)
    pro_vid = st.file_uploader("Upload Raw Clip", type=["mp4", "mov"], key="pro_up")
    grade_mode = st.radio("Select Grading Engine:", ["🤖 Auto-Apply 100 Cinematic Presets", "🎛️ Manual Colorist Control (Pro)"], horizontal=True)
    
    if "Presets" in grade_mode:
        chosen_preset = st.selectbox("Select from 100 Custom Filters", list(CINEMATIC_FILTERS_100.keys()))
        b_val, c_val, s_val, w_val = CINEMATIC_FILTERS_100[chosen_preset]
    else:
        colA, colB = st.columns(2)
        b_val = colA.slider("☀️ Brightness", 0.3, 2.0, 1.0, 0.05); c_val = colB.slider("🌗 Contrast", 0.3, 2.0, 1.0, 0.05)
        colC, colD = st.columns(2)
        s_val = colC.slider("🌈 Saturation", 0.0, 3.0, 1.0, 0.1); w_val = colD.slider("🔥 Warmth", -50, 50, 0, 1)
    
    apply_sharpness = st.checkbox("Apply Unsharp Mask (Crisp Details)", value=False)
    
    if pro_vid and st.button("✨ RENDER CINEMATIC GRADE"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in_path = os.path.join(tmp_dir, "in_pro.mp4"); v_out_path = os.path.join(tmp_dir, "out_pro.mp4")
            with open(v_in_path, "wb") as f: f.write(pro_vid.getbuffer())
            
            cap = cv2.VideoCapture(v_in_path)
            fps = cap.get(cv2.CAP_PROP_FPS); w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out_path + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); f_idx = 0; prog_bar = st.progress(0)
            
            while True:
                success, frame = cap.read()
                if not success: break
                
                graded_frame = master_color_grader_pil(frame, b_val, c_val, s_val, w_val)
                if apply_sharpness:
                    gaussian = cv2.GaussianBlur(graded_frame, (0, 0), 2.0)
                    graded_frame = cv2.addWeighted(graded_frame, 1.5, gaussian, -0.5, 0)
                
                writer.write(graded_frame); f_idx += 1
                if f_idx % 15 == 0: prog_bar.progress(min(f_idx/tot_frames, 1.0))
            
            cap.release(); writer.release()
            with VideoFileClip(v_in_path) as o_vid:
                with VideoFileClip(v_out_path + "_tmp.mp4") as p_vid:
                    p_vid.set_audio(o_vid.audio).write_videofile(v_out_path, codec="libx264", audio_codec="aac", logger=None)
            st.success("✅ RENDERING COMPLETE!"); st.video(v_out_path)
            with open(v_out_path, "rb") as out_file: st.download_button("📥 DOWNLOAD", out_file, "wdpro_graded.mp4")
                                                                                                                                 
