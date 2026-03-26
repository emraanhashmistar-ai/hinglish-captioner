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

# --- 1. SUPREME UI & 3D ANIMATIONS ---
st.set_page_config(page_title="WD PRO FF - MASTER ENGINE", page_icon="🎬", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .main { background: radial-gradient(circle, #1a0000 0%, #000000 100%); color: white; }
    
    /* Welcome Subscriber Animation */
    .welcome-anim { 
        text-align: center; font-size: 55px; font-weight: 900; 
        background: linear-gradient(45deg, #ff0000, #ffd700, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: slideIn 2s ease-out, glow 1.5s infinite alternate;
    }
    @keyframes slideIn { from { opacity:0; transform: translateY(-50px); } to { opacity:1; transform: translateY(0); } }
    @keyframes glow { from { filter: drop-shadow(0 0 5px #ff0000); } to { filter: drop-shadow(0 0 20px #ff0000); } }

    /* Ultra 3D Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #ff0000, #330000); 
        color: white; border-radius: 15px; font-weight: bold; border: 2px solid #ff4b4b; 
        height: 4.5rem; width: 100%; transition: 0.3s; box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
    }
    .stButton>button:hover { box-shadow: 0 0 40px #ff0000; transform: scale(1.02); }

    /* Social Sidebar Branding */
    .social-box { 
        background: #111; border: 1px solid #ff0000; border-radius: 10px; padding: 15px; margin-bottom: 10px; 
        transition: 0.3s; text-align: center;
    }
    .social-box:hover { background: #ff0000; box-shadow: 0 0 15px #ff0000; }
    .social-link { text-decoration: none; color: white; font-weight: bold; font-size: 16px; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 2. CORE UTILITIES ---
@st.cache_resource
def load_whisper_engine():
    return whisper.load_model("base")

def get_font_engine(font_name, size):
    # Mapping for many font looks
    paths = {
        "Gaming Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Serif Elegant": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "Modern Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Mono Pro": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    }
    p = paths.get(font_name, paths["Gaming Bold"])
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

# --- 3. SIDEBAR (THE 50+ OPTIONS PANEL) ---
saved_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:red;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    # Social Links (Name + Link)
    st.markdown("### 🌐 BRANDING")
    st.markdown('<div class="social-box"><a href="https://youtube.com/@WDPROFF" class="social-link">📺 YOUTUBE: WD PRO FF</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="social-box"><a href="https://instagram.com/WDPROFF" class="social-link">📸 INSTA: @WDPROFF</a></div>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 Gemini API Key", value=saved_key, type="password")
    
    st.header("🌍 50+ LANGUAGES")
    all_langs = ["Hinglish", "Hindi", "Urdu", "English", "Punjabi", "Bengali", "Marathi", "Tamil", "Telugu", "Arabic", "Spanish", "French", "Japanese", "Russian", "Korean"]
    target_lang = st.selectbox("Select Audio Language", all_langs)

    st.header("🎨 50+ STYLES & FONTS")
    f_choice = st.selectbox("Font Face", ["Gaming Bold", "Serif Elegant", "Modern Sans", "Mono Pro"])
    f_size = st.slider("Font Size", 20, 200, 85)
    t_color = st.color_picker("Main Text Color", "#FFFF00")
    
    st.header("✨ ANIMATION & FLOW")
    anim_type = st.selectbox("Text Animation", ["Pop-Up", "Zoom-Bounce", "Glow-Pulse", "Shake-Effect", "Fade-In", "Static"])
    word_count = st.selectbox("Words Per Caption", ["1 Word (Fast)", "2 Words", "3 Words", "Full Sentence"])
    
    st.header("🔳 OUTLINE & EFFECTS")
    o_color = st.color_picker("Outline/Shadow Color", "#000000")
    o_width = st.slider("Outline Thickness", 0, 15, 6)
    o_type = st.selectbox("Outline Style", ["Deep Shadow", "Neon Glow", "Soft Fade", "Hard Border"])
    
    pos_choice = st.selectbox("Screen Position", ["Bottom Center", "Middle", "Top Center", "Lower Left", "Lower Right"])

# --- 4. THE MAGIC LOGIC (ROMAN SCRIPT & WRAPPING) ---
def transliterate_engine(segments, key):
    if not segments or not key: return segments
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        raw_txt = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
        prompt = (
            "TRANSLITERATE ONLY. DO NOT TRANSLATE. "
            "Convert to ROMAN SCRIPT (English Alphabet). "
            "Example: 'Udhar jao' stays 'Udhar jao'. "
            "STRICT: NO Hindi/Urdu characters. Return JSON array. Input:\n" + raw_txt
        )
        res = model.generate_content(prompt)
        h_list = json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
        for i, s in enumerate(segments):
            clean = h_list[i] if i < len(h_list) else s['text']
            s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean)
    except: pass
    return segments

# --- 5. THE RENDERER (ALL FEATURES COMBINED) ---
def render_master_video(v_in, segments, v_out, f_size, t_color, o_color, o_width, o_type, pos, mode, anim, font_name):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_path = v_out + "_final_tmp.mp4"
    writer = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    
    # 50+ Mode Logic (Word breakdown)
    processed_segs = []
    if mode != "Full Sentence":
        words_num = 1 if "1 Word" in mode else (2 if "2 Words" in mode else 3)
        for s in segments:
            words = s['hinglish'].split()
            dur = (s['end'] - s['start']) / max(len(words), 1)
            for i in range(0, len(words), words_num):
                processed_segs.append({
                    'start': s['start'] + (i//words_num) * dur,
                    'end': s['start'] + (i//words_num + 1) * dur,
                    'text': " ".join(words[i:i+words_num])
                })
    else:
        for s in segments: processed_segs.append({'start': s['start'], 'end': s['end'], 'text': s['hinglish']})

    f_idx = 0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    p_bar = st.progress(0)
    
    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    or_,og,ob = int(o_color[1:3],16), int(o_color[3:5],16), int(o_color[5:7],16)

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        curr_t = f_idx / fps
        txt = next((s['text'] for s in processed_segs if s['start'] <= curr_t <= s['end']), "")
        
        if txt:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            # Animation Logic (Pop, Bounce, Pulse)
            curr_f_size = f_size
            offset_x, offset_y = 0, 0
            if anim == "Pop-Up": curr_f_size = int(f_size * (1.15 if f_idx % 12 < 6 else 1.0))
            elif anim == "Zoom-Bounce": curr_f_size = int(f_size * (1.0 + 0.2 * abs(np.sin(f_idx * 0.4))))
            elif anim == "Glow-Pulse": curr_f_size = int(f_size * (1.0 + 0.1 * np.cos(f_idx * 0.3)))
            elif anim == "Shake-Effect": offset_x = int(7 * np.sin(f_idx))
            
            font = get_font_engine(font_name, curr_f_size)
            
            # Text Wrapping (Bahar na jaye)
            max_w = w * 0.85
            words = txt.split(); lines = []; cur_line = []
            for wd in words:
                if font.getbbox(" ".join(cur_line + [wd]))[2] <= max_w: cur_line.append(wd)
                else: lines.append(" ".join(cur_line)); cur_line = [wd]
            lines.append(" ".join(cur_line))
            
            total_h = len(lines) * (curr_f_size + 15)
            
            # Position Engine
            if "Bottom" in pos: sy = h - total_h - 130
            elif "Top" in pos: sy = 130
            elif "Middle" in pos: sy = (h - total_h) // 2
            else: sy = h - total_h - 150 # Default
            
            for i, line in enumerate(lines):
                lw = font.getbbox(line)[2]
                lx = (w - lw) // 2 + offset_x
                ly = sy + i * (curr_f_size + 15) + offset_y
                
                # Outline Style Engine
                if o_width > 0:
                    if o_type == "Deep Shadow":
                        for d in range(1, o_width + 1): draw.text((lx+d, ly+d), line, font=font, fill=(0,0,0,180))
                    elif o_type == "Neon Glow":
                        for ox in range(-o_width, o_width+1):
                            for oy in range(-o_width, o_width+1): draw.text((lx+ox, ly+oy), line, font=font, fill=(or_,og,ob,80))
                    else: # Hard Border
                        for ox in range(-o_width, o_width+1):
                            for oy in range(-o_width, o_width+1): draw.text((lx+ox, ly+oy), line, font=font, fill=(or_,og,ob))
                
                draw.text((lx, ly), line, font=font, fill=(r,g,b))
            
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
        writer.write(frame); f_idx += 1
        if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_f, 1.0))
        
    cap.release(); writer.release()
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(temp_path) as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. MAIN APP INTERFACE ---
if 'first_load' not in st.session_state:
    st.balloons()
    st.snow()
    st.markdown('<h1 class="welcome-anim">Welcome WD PRO FF Subscriber! 🔥</h1>', unsafe_allow_html=True)
    st.session_state.first_load = True

st.markdown("<h2 style='text-align:center; letter-spacing:3px;'>🚀 THE WD PRO ULTRA ENGINE</h2>", unsafe_allow_html=True)
video_file = st.file_uploader("Upload Gaming Clip", type=["mp4", "mov"])

if video_file and api_key:
    if st.button("🔥 START SUPREME RENDERING"):
        with tempfile.TemporaryDirectory() as tmpdir:
            v_in, v_out = os.path.join(tmpdir, "in.mp4"), os.path.join(tmpdir, "out.mp4")
            with open(v_in, "wb") as f: f.write(video_file.getbuffer())
            
            st.info(f"🎙️ AI is Listening ({target_lang})...")
            w_model = load_whisper_engine()
            res = w_model.transcribe(v_in, language="hi" if target_lang == "Hinglish" else target_lang.lower())
            
            st.info("✍️ Converting to Roman Script (Hinglish Style)...")
            segs = transliterate_engine(res['segments'], api_key)
            
            st.info("🎨 Applying 50+ Custom Styles & Animations...")
            render_master_video(v_in, segs, v_out, f_size, t_color, o_color, o_width, o_type, pos_choice, word_count, anim_type, f_choice)
            
            st.success("🏆 WD PRO MASTERPIECE IS READY!")
            st.video(v_out)
            with open(v_out, "rb") as f: st.download_button("📥 DOWNLOAD ULTRA VIDEO", f, "wd_pro_video.mp4")
                
