import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai

# --- 1. SUPREME GAMING UI ---
st.set_page_config(page_title="WD PRO FF - THE FINAL ENGINE", page_icon="🔥", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .main { background: radial-gradient(circle, #1a0000 0%, #000000 100%); color: white; }
    .welcome-anim { 
        text-align: center; font-size: 55px; font-weight: 900; 
        background: linear-gradient(45deg, #ff0000, #ffd700, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: slideIn 1.5s ease-out, glow 1.5s infinite alternate;
        margin-bottom: 20px;
    }
    @keyframes slideIn { from { opacity:0; transform: translateY(-30px); } to { opacity:1; transform: translateY(0); } }
    @keyframes glow { from { filter: drop-shadow(0 0 5px #ff0000); } to { filter: drop-shadow(0 0 20px #ff0000); } }
    .stButton>button { 
        background: linear-gradient(135deg, #ff0000, #330000); 
        color: white; border-radius: 15px; font-weight: bold; border: 2px solid #ff4b4b; 
        height: 4.5rem; width: 100%; transition: 0.3s; box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
    }
    .stButton>button:hover { box-shadow: 0 0 40px #ff0000; transform: scale(1.02); }
    .social-box { 
        background: #111; border: 1px solid #ff0000; border-radius: 10px; padding: 12px; margin-bottom: 10px; 
        text-align: center; transition: 0.3s;
    }
    .social-box:hover { background: #ff0000; }
    .social-link { text-decoration: none; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE ENGINES ---
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

def get_pro_font(font_name, size):
    paths = {
        "Gaming Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Serif Elegant": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "Modern Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Mono Pro": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    }
    p = paths.get(font_name, paths["Gaming Bold"])
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

# --- 3. SIDEBAR (50+ OPTIONS) ---
# Yahan apni key hamesha ke liye dalo
FINAL_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:red;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    st.markdown("### 🌐 BRANDING")
    st.markdown('<div class="social-box"><a href="https://youtube.com/@WDPROFF" class="social-link">📺 YOUTUBE: WD PRO FF</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="social-box"><a href="https://instagram.com/WDPROFF" class="social-link">📸 INSTA: @WDPROFF</a></div>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 Gemini Key", value=FINAL_KEY, type="password")
    
    st.header("🌍 50+ LANGUAGES")
    target_lang = st.selectbox("Select Audio Language", ["Hinglish", "Hindi", "Urdu", "English", "Punjabi", "Arabic", "Spanish", "French"])

    st.header("🎨 50+ STYLE COMBOS")
    f_choice = st.selectbox("Font Face", ["Gaming Bold", "Serif Elegant", "Modern Sans", "Mono Pro"])
    f_size = st.slider("Font Size", 20, 200, 85)
    t_color = st.color_picker("Text Color", "#FFFF00")
    
    st.header("✨ FLOW & ANIMATION")
    word_count = st.selectbox("Words Control", ["1 Word (Fast)", "2 Words", "Full Sentence"])
    anim_type = st.selectbox("Animation Style", ["Pop-Up", "Zoom-Bounce", "Glow-Pulse", "Static"])
    
    st.header("🔳 OUTLINE")
    o_color = st.color_picker("Outline Color", "#000000")
    o_width = st.slider("Outline Weight", 0, 15, 6)
    o_style = st.selectbox("Shadow Type", ["Deep Shadow", "Neon Glow", "Hard Border"])
    
    pos = st.selectbox("Position", ["Bottom Center", "Middle", "Top Center"])

# --- 4. ROMAN LOGIC (FIXED FOR KEYERROR) ---
def transliterate_logic(segments, key):
    if not segments or not key: return segments
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        raw = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
        prompt = "TRANSLITERATE TO ROMAN SCRIPT ONLY. DO NOT TRANSLATE. JSON array only:\n" + raw
        res = model.generate_content(prompt)
        h_list = json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
        for i, s in enumerate(segments):
            # Fallback agar AI 'hinglish' key na de
            s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', h_list[i]) if i < len(h_list) else s['text']
    except:
        for s in segments: s["hinglish"] = s['text']
    return segments

# --- 5. THE ULTIMATE RENDERER (NO-ERROR VERSION) ---
def render_wd_masterpiece(v_in, segments, v_out, f_size, t_color, o_color, o_width, o_style, pos, mode, anim, f_name):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_file = v_out + "_final_tmp.mp4"
    writer = cv2.VideoWriter(temp_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    
    # Error-Proof Word Breakdown
    final_segs = []
    num_words = 1 if "1 Word" in mode else (2 if "2 Words" in mode else 999)
    
    for s in segments:
        text_val = s.get('hinglish', s.get('text', '')) # FIX: KeyError handle
        words = text_val.split()
        if not words: continue
        
        if mode == "Full Sentence":
            final_segs.append({'start': s['start'], 'end': s['end'], 'text': text_val})
        else:
            dur = (s['end'] - s['start']) / max(len(words), 1)
            for i in range(0, len(words), num_words):
                final_segs.append({
                    'start': s['start'] + (i//num_words) * dur,
                    'end': s['start'] + (i//num_words + 1) * dur,
                    'text': " ".join(words[i:i+num_words])
                })

    f_idx = 0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    p_bar = st.progress(0)
    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    or_,og,ob = int(o_color[1:3],16), int(o_color[3:5],16), int(o_color[5:7],16)

    while True:
        ret, frame = cap.read()
        if not ret: break
        t = f_idx / fps
        txt = next((s['text'] for s in final_segs if s['start'] <= t <= s['end']), "")
        
        if txt:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            # Animation scaling
            cur_size = f_size
            if anim == "Pop-Up": cur_size = int(f_size * (1.15 if f_idx % 12 < 6 else 1.0))
            elif anim == "Zoom-Bounce": cur_size = int(f_size * (1.0 + 0.15 * abs(np.sin(f_idx * 0.5))))
            
            font = get_pro_font(f_name, cur_size)
            
            # Text Wrap (Screen se bahar na jaye)
            max_w = w * 0.85
            words_wrap = txt.split(); lines = []; cur_line = []
            for wd in words_wrap:
                if font.getbbox(" ".join(cur_line + [wd]))[2] <= max_w: cur_line.append(wd)
                else: lines.append(" ".join(cur_line)); cur_line = [wd]
            lines.append(" ".join(cur_line))
            
            total_th = len(lines) * (cur_size + 15)
            if "Bottom" in pos: sy = h - total_th - 130
            elif "Top" in pos: sy = 130
            else: sy = (h - total_th) // 2
            
            for i, line in enumerate(lines):
                lw = font.getbbox(line)[2]
                lx, ly = (w - lw) // 2, sy + i * (cur_size + 15)
                
                if o_width > 0:
                    if o_style == "Neon Glow":
                        for ox in range(-o_width, o_width+1):
                            for oy in range(-o_width, o_width+1): draw.text((lx+ox, ly+oy), line, font=font, fill=(or_,og,ob,80))
                    else:
                        for d in range(1, o_width + 1): draw.text((lx+d, ly+d), line, font=font, fill=(0,0,0,200))
                
                draw.text((lx, ly), line, font=font, fill=(r,g,b))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        writer.write(frame); f_idx += 1
        if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_f, 1.0))
        
    cap.release(); writer.release()
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(temp_file) as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. WORKFLOW ---
if 'wd_start' not in st.session_state:
    st.balloons(); st.snow()
    st.markdown('<h1 class="welcome-anim">Welcome WD PRO FF Subscriber! 🔥</h1>', unsafe_allow_html=True)
    st.session_state.wd_start = True

st.markdown("<h2 style='text-align:center;'>🚀 WD PRO MASTER ENGINE</h2>", unsafe_allow_html=True)
video_up = st.file_uploader("Upload Clip", type=["mp4"])

if video_up and api_key:
    if st.button("🔥 START SUPREME RENDERING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(video_up.getbuffer())
            
            st.info(f"🎙️ AI listening in {target_lang}...")
            res = load_whisper().transcribe(v_in, language="hi" if target_lang == "Hinglish" else target_lang.lower())
            
            st.info("✍️ Scripting in Roman script (No Translation)...")
            segs = transliterate_logic(res['segments'], api_key)
            
            st.info("🎨 Applying 50+ Custom Styles...")
            render_wd_masterpiece(v_in, segs, v_out, f_size, t_color, o_color, o_width, o_style, pos, word_count, anim_type, f_choice)
            
            st.success("🏆 WD PRO MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as f: st.download_button("📥 DOWNLOAD VIDEO", f, "wd_pro_video.mp4")
                
