import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai

# --- 1. BASIC CONFIG ---
st.set_page_config(page_title="WD PRO FF OFFICIAL", page_icon="🔥", layout="wide")

# --- 2. ADVANCED UI, SOUND & ANIMATION (CSS/JS) ---
st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.tagName === 'A') {
            document.getElementById('clickSound').play();
        }
    });
    </script>
    <style>
    .main { background: #0a0a0c; color: #ffffff; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff0000, #ff4b4b); 
        color: white; border-radius: 10px; font-weight: bold; border: none; 
        height: 3.5rem; width: 100%; transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 0 20px #ff0000; }
    .stButton>button:active { transform: scale(0.95); }
    
    .social-btn { 
        text-decoration: none; color: white; background: #161625; 
        display: block; padding: 12px; border-radius: 8px; text-align: center; 
        margin-bottom: 10px; border: 1px solid #ff0000; transition: 0.3s;
    }
    .social-btn:hover { background: #ff0000; box-shadow: 0 0 15px #ff0000; }
    
    .welcome-title { 
        text-align: center; font-size: 55px; font-weight: 900; 
        color: #ff0000; text-shadow: 0 0 15px #ff0000;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. WELCOME EFFECTS ---
if 'first_time' not in st.session_state:
    st.balloons()
    st.snow()
    st.markdown('<h1 class="welcome-title">WELCOME TO WD PRO FF</h1>', unsafe_allow_html=True)
    st.session_state.first_time = True

# --- 4. SIDEBAR (Links & Key) ---
saved_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ff0000;'>WD PRO FF</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    st.markdown("### 🔗 Connect With Me")
    # YAHAN APNE LINKS DALO
    st.markdown('<a href="https://youtube.com/@WDPROFF" target="_blank" class="social-btn">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/WDPROFF" target="_blank" class="social-btn">📸 Instagram</a>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 Gemini API Key", value=saved_key, type="password")
    f_size = st.slider("Font Size", 20, 100, 50)
    t_color = st.color_picker("Caption Color", "#FFFF00")

# --- 5. CAPTION LOGIC (STRICT ROMAN) ---
def get_roman_hinglish(segments, key):
    if not segments or not key: return segments
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    text_to_convert = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
    prompt = "Convert to ROMAN SCRIPT (English letters) ONLY. No Hindi/Urdu text. Example: 'Kya haal hai'. JSON array only:\n" + text_to_convert
    try:
        res = model.generate_content(prompt)
        h_list = json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
        for i, s in enumerate(segments): s["hinglish"] = h_list[i] if i < len(h_list) else s["text"]
    except: pass
    return segments

def process_video(v_in, segments, v_out, f_size, t_color):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_v = v_out + "_temp.mp4"
    writer = cv2.VideoWriter(temp_v, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", f_size)
    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    
    f_idx = 0
    prog = st.progress(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        curr_t = f_idx / fps
        txt = next((s.get('hinglish', s['text']) for s in segments if s['start'] <= curr_t <= s['end']), "")
        if txt:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            tw = draw.textbbox((0,0), txt, font=font)[2]
            tx, ty = (w-tw)//2, h-f_size-100
            for o in range(-2,3): 
                for o2 in range(-2,3): draw.text((tx+o, ty+o2), txt, font=font, fill=(0,0,0))
            draw.text((tx, ty), txt, font=font, fill=(r,g,b))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(frame); f_idx += 1
        if f_idx % 25 == 0: prog.progress(min(f_idx/int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1.0))
    cap.release(); writer.release()
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(temp_v) as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. MAIN APP INTERFACE ---
st.header("🎮 WD PRO CAPTIONER")
uploaded = st.file_uploader("Upload Video", type=["mp4"])

if uploaded and api_key:
    if st.button("🚀 START PRO MAGIC"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(uploaded.getbuffer())
            st.info("🎙️ Hearing Audio...")
            res = whisper.load_model("base").transcribe(v_in)
            st.info("✍️ Converting to Roman English...")
            segs = get_roman_hinglish(res['segments'], api_key)
            st.info("🔥 Adding Pro Captions...")
            process_video(v_in, segs, v_out, f_size, t_color)
            st.success("✅ DONE! Check Video Below:")
            st.video(v_out)
            with open(v_out, "rb") as f: st.download_button("📥 DOWNLOAD NOW", f, "wd_pro_video.mp4")
                
