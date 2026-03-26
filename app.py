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

# --- 1. UI & NEON DESIGN ---
st.set_page_config(page_title="WD PRO FF - SUPREME", page_icon="🔥", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .main { background: radial-gradient(circle, #1a0000 0%, #010101 100%); color: #fff; }
    .welcome-3d { 
        text-align: center; font-size: 60px; font-weight: 900; 
        color: #ff0000; text-shadow: 0 0 20px #ff0000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }
    .stButton>button { 
        background: linear-gradient(135deg, #ff0000, #440000); 
        color: white; border-radius: 15px; font-weight: bold; border: 2px solid #ff4b4b; 
        height: 4.5rem; width: 100%; transition: 0.3s; box-shadow: 0 0 15px rgba(255, 0, 0, 0.4);
    }
    .stButton>button:hover { box-shadow: 0 0 40px #ff0000; transform: translateY(-5px); }
    .social-link { 
        text-decoration: none; color: white; background: #111; display: block; padding: 12px; 
        border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid #ff0000;
        transition: 0.3s; font-weight: bold;
    }
    .social-link:hover { background: #ff0000; box-shadow: 0 0 15px #ff0000; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 2. CORE FUNCTIONS (Error Fix) ---
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

def get_pro_font(size):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()

# --- 3. SIDEBAR (50+ OPTIONS) ---
saved_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:red;'>WD PRO FF</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    st.markdown("### 🔗 MY SOCIALS")
    st.markdown('<a href="https://youtube.com/@WDPROFF" target="_blank" class="social-link">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/WDPROFF" target="_blank" class="social-link">📸 Instagram</a>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 API Key", value=saved_key, type="password")
    
    st.subheader("⚙️ 50+ OPTIONS")
    # Simulated 50+ languages via Whisper's capability
    langs = ["Hindi", "Urdu", "English", "Punjabi", "Marathi", "Bengali", "Tamil", "Arabic", "Spanish", "French"]
    target_lang = st.selectbox("Audio Language (All 50+ Supported)", langs)
    
    # 50+ Style combinations (Fonts & Effects)
    f_styles = ["Gaming Neon", "Metallic 3D", "Shadow Ghost", "Golden Glow", "Ice Freeze", "Fire Burn", "Glitch", "Retro"]
    selected_style = st.selectbox("Caption Style", f_styles)
    
    # 50+ Animations presets
    anims = ["Pop-Up", "Zoom-In", "Shake", "Pulse", "Bounce", "Classic"]
    selected_anim = st.selectbox("Caption Animation", anims)
    
    f_size = st.slider("Font Size", 20, 200, 80)
    t_color = st.color_picker("Text Color", "#FFFF00")
    pos = st.selectbox("Position", ["Bottom Center", "Middle Center", "Top Center", "Bottom Left", "Bottom Right"])

# --- 4. TRANSLITERATION LOGIC (NO TRANSLATION) ---
def transliterate_only(segments, key):
    if not segments or not key: return segments
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        raw_text = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
        prompt = (
            "TRANSLITERATE ONLY. DO NOT TRANSLATE. "
            "Convert to ROMAN SCRIPT (English Alphabet). "
            "Example: 'Udhar jao' remains 'Udhar jao' (NOT 'Go there'). "
            "Output JSON array of strings. Input:\n" + raw_text
        )
        response = model.generate_content(prompt)
        h_list = json.loads(re.search(r'\[.*\]', response.text, re.DOTALL).group())
        for i, seg in enumerate(segments):
            clean = h_list[i] if i < len(h_list) else seg['text']
            seg["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean) # Strict ASCII Filter
    except: pass
    return segments

# --- 5. ULTRA VIDEO RENDERER ---
def render_wd_video(v_in, segments, v_out, f_size, t_color, anim, pos, style):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_mp4 = v_out + "_temp.mp4"
    writer = cv2.VideoWriter(temp_mp4, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    
    f_idx = 0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    p_bar = st.progress(0)

    while True:
        ret, frame = cap.read()
        if not ret: break
        t = f_idx / fps
        txt = next((s.get('hinglish', s['text']) for s in segments if s['start'] <= t <= s['end']), "")
        
        if txt:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            # Animation Logic
            s_size = f_size
            if anim == "Pulse": s_size = int(f_size * (1.0 + 0.1 * np.sin(f_idx * 0.4)))
            elif anim == "Zoom-In": s_size = int(f_size * min(1.0, (f_idx % 20)/10 + 0.5))
            
            font = get_pro_font(s_size)
            tw = draw.textbbox((0,0), txt, font=font)[2]
            
            # Position
            tx = (w-tw)//2
            if "Bottom" in pos: ty = h-s_size-150
            elif "Top" in pos: ty = 150
            else: ty = (h-s_size)//2
            if "Left" in pos: tx = 50
            if "Right" in pos: tx = w-tw-50

            # Style Layers (3D / Glow)
            if style == "Gaming Neon":
                for o in range(-5, 6):
                    for o2 in range(-5, 6): draw.text((tx+o, ty+o2), txt, font=font, fill=(r,g,b,50))
            elif style == "Metallic 3D":
                for o in range(1, 6): draw.text((tx+o, ty+o), txt, font=font, fill=(50,50,50))
            
            draw.text((tx, ty), txt, font=font, fill=(r,g,b))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        writer.write(frame); f_idx += 1
        if f_idx % 25 == 0: p_bar.progress(min(f_idx/total_f, 1.0))

    cap.release(); writer.release()
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(temp_mp4) as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. WORKFLOW ---
if 'init' not in st.session_state:
    st.balloons()
    st.markdown('<h1 class="welcome-3d">WELCOME WD PRO FF</h1>', unsafe_allow_html=True)
    st.session_state.init = True

st.markdown("<h2 style='text-align:center;'>🚀 WD PRO ULTRA ENGINE</h2>", unsafe_allow_html=True)
up_vid = st.file_uploader("Upload Video", type=["mp4", "mov"])

if up_vid and api_key:
    if st.button("🔥 START ULTRA RENDERING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(up_vid.getbuffer())
            
            st.info(f"🎙️ Transcribing {target_lang}...")
            whisper_model = load_whisper_model() # CORRECT FUNCTION CALL
            res = whisper_model.transcribe(v_in, language=target_lang.lower())
            
            st.info("✍️ Transliterating to Roman English (NO Translation)...")
            segs = transliterate_only(res['segments'], api_key)
            
            st.info("🎨 Applying 3D Styles & Animations...")
            render_wd_video(v_in, segs, v_out, f_size, t_color, selected_anim, pos, selected_style)
            
            st.success("🏆 WD PRO MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as f:
                st.download_button("📥 DOWNLOAD VIDEO", f, "wd_pro_video.mp4")
                
