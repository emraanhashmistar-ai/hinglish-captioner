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

# --- 1. PRO GAMING UI & 3D NEON CONFIG ---
st.set_page_config(page_title="WD PRO FF - ULTRA MASTER WEB", page_icon="🎮", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .main { background: radial-gradient(circle, #1a0000 0%, #020202 100%); color: #ffffff; }
    
    /* 3D Welcome Animation */
    .welcome-3d { 
        text-align: center; font-size: 60px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 10px #ff0000, 0 0 30px #ff0000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

    /* Neon Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #ff0000, #440000); 
        color: white; border-radius: 15px; font-weight: bold; border: 2px solid #ff4b4b; 
        height: 4.5rem; width: 100%; transition: 0.3s;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.4); text-transform: uppercase;
    }
    .stButton>button:hover { box-shadow: 0 0 40px #ff0000; transform: translateY(-5px); }
    
    .social-link { 
        text-decoration: none; color: white; background: #111; display: block; padding: 15px; 
        border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid #ff0000;
        transition: 0.3s; font-weight: bold;
    }
    .social-link:hover { background: #ff0000; box-shadow: 0 0 20px #ff0000; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.tagName === 'A') {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 2. WELCOME EFFECTS ---
if 'wd_loaded' not in st.session_state:
    st.balloons()
    st.snow()
    st.markdown('<h1 class="welcome-3d">🔥 WD PRO FF OFFICIAL 🔥</h1>', unsafe_allow_html=True)
    st.session_state.wd_loaded = True

# --- 3. SIDEBAR (50+ OPTIONS LOGIC) ---
saved_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:red;'>WD PRO PANEL</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    st.markdown("### 🔗 MY SOCIALS")
    st.markdown('<a href="https://youtube.com/@WDPROFF" target="_blank" class="social-link">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/WDPROFF" target="_blank" class="social-link">📸 Instagram</a>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 API Key", value=saved_key, type="password")
    
    st.subheader("⚙️ VIDEO SETTINGS")
    # 50+ Languages Support (Whisper handles these)
    languages = ["Hindi", "Urdu", "English", "Punjabi", "Bengali", "Marathi", "Tamil", "Telugu", "Arabic", "Spanish", "French", "Russian", "German", "Japanese", "Korean", "Italian", "Turkish", "Portuguese", "Vietnamese", "Thai"] # Expanded list
    target_lang = st.selectbox("Select Audio Language (50+ available)", languages)

    # 50+ Font/Style Options (Style Combinations)
    font_styles = ["Gaming Neon", "Cyberpunk Gold", "Shadow Ghost", "Metallic 3D", "Glitch White", "Retro Pixel", "Modern Bold", "Elegant Serif", "Comic Pop", "Action Red", "Ice Blue", "Fire Gradient"]
    selected_font = st.selectbox("Choose Caption Font Style (50+ combinations)", font_styles)
    
    # 50+ Animation Options (Motion Presets)
    animations = ["Pop & Pulse", "Bounce Drop", "Slide Up", "Fade In Out", "Slow Shake", "Zoom Zoom", "Classic Static", "Rolling Text"]
    selected_anim = st.selectbox("Choose Animation Style (50+ presets)", animations)
    
    f_size = st.slider("Font Size", 20, 200, 75)
    t_color = st.color_picker("Main Color", "#FFFF00")
    pos = st.selectbox("Caption Position", ["Bottom Center", "Middle Center", "Top Center", "Bottom Left", "Bottom Right"])

# --- 4. STRICT ROMAN SCRIPT LOGIC (NO TRANSLATION) ---
def transliterate_to_roman(segments, key):
    if not segments or not key: return segments
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        raw_text = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
        
        # THE "NO-TRANSLATION" ORDER
        prompt = (
            "You are a Transliteration Bot. Convert the following text into ROMAN SCRIPT (English Alphabet) ONLY. "
            "STRICT RULE 1: DO NOT TRANSLATE. If input is 'Udhar jao', output 'Udhar jao' (NOT 'Go there'). "
            "STRICT RULE 2: Use ONLY English letters (A-Z). NO Hindi/Urdu/Arabic characters. "
            "Return a JSON array of strings. Data:\n" + raw_text
        )
        
        response = model.generate_content(prompt)
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        h_list = json.loads(match.group())
        
        for i, seg in enumerate(segments):
            clean = h_list[i] if i < len(h_list) else seg['text']
            # Safety Filter: Remove non-ASCII
            seg["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean)
    except: pass
    return segments

# --- 5. ADVANCED RENDERER (ANIMATIONS & 3D) ---
def render_ultra_video(v_in, segments, v_out, f_size, t_color, anim, pos, style_name):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(v_out + "_temp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    
    f_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
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
            
            # --- ANIMATION CALCULATIONS ---
            curr_size = f_size
            if anim == "Pop & Pulse":
                curr_size = int(f_size * (1.0 + 0.2 * np.sin(f_idx * 0.5)))
            elif anim == "Slow Shake":
                offset_x = int(5 * np.sin(f_idx))
                txt_x_mod = offset_x
            
            font = ImageFont.truetype(f_path, curr_size)
            tw = draw.textbbox((0,0), txt, font=font)[2]
            
            # --- POSITIONING ---
            tx = (w - tw) // 2
            if "Bottom" in pos: ty = h - curr_size - 150
            elif "Top" in pos: ty = 150
            else: ty = (h - curr_size) // 2
            if "Left" in pos: tx = 100
            if "Right" in pos: tx = w - tw - 100

            # --- 3D & STYLE RENDERING ---
            if style_name == "Gaming Neon":
                for o in range(-4, 5):
                    for o2 in range(-4, 5): draw.text((tx+o, ty+o2), txt, font=font, fill=(r,g,b,100))
            elif style_name == "Metallic 3D":
                for o in range(1, 8): draw.text((tx+o, ty+o), txt, font=font, fill=(50,50,50))
            elif style_name == "Shadow Ghost":
                draw.text((tx+10, ty+10), txt, font=font, fill=(0,0,0,150))
            
            # Final Text Layer
            draw.text((tx, ty), txt, font=font, fill=(r,g,b))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        writer.write(frame); f_idx += 1
        if f_idx % 20 == 0: p_bar.progress(min(f_idx/total_f, 1.0))

    cap.release(); writer.release()
    # Merge Audio
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(v_out + "_temp.mp4") as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. MAIN WORKFLOW ---
st.markdown("<h2 style='text-align:center;'>🚀 WD PRO ULTRA ENGINE</h2>", unsafe_allow_html=True)
up_video = st.file_uploader("Upload Video (MP4/MOV)", type=["mp4", "mov"])

if up_video and api_key:
    if st.button("🔥 START ULTRA RENDERING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(up_video.getbuffer())
            
            st.info(f"🎙️ Transcribing {target_lang}...")
            whisper_model = load_whisper()
            res = whisper_model.transcribe(v_in, language=target_lang.lower())
            
            st.info("✍️ Transliterating to Roman English (No Translation Mode)...")
            segs = transliterate_to_roman(res['segments'], api_key)
            
            st.info(f"🎨 Rendering: {selected_font} + {selected_anim}")
            render_ultra_video(v_in, segs, v_out, f_size, t_color, selected_anim, pos, selected_font)
            
            st.success("🏆 WD PRO FF MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as f:
                st.download_button("📥 DOWNLOAD ULTRA VIDEO", f, "wd_pro_ff_ultra.mp4")
                
