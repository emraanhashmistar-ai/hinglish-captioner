import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
import google.generativeai as genai
from gtts import gTTS # Dubbing ke liye

# --- 1. SUPREME UI CONFIG ---
st.set_page_config(page_title="WD PRO FF - ALL IN ONE", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .main { background: #050505; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border: 1px solid #ff0000; border-radius: 10px;
        padding: 10px 20px; color: white; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #ff0000 !important; }
    .welcome-title { text-align: center; font-size: 50px; color: #ff0000; text-shadow: 0 0 15px #ff0000; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    </style>
""", unsafe_allow_html=True)

# --- 2. SHARED ENGINES ---
@st.cache_resource
def load_whisper(): return whisper.load_model("base")

def get_pro_font(size):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

# --- 3. SIDEBAR BRANDING ---
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
with st.sidebar:
    st.image("https://img.icons8.com/color/144/free-fire.png")
    st.title("WD PRO PANEL")
    st.markdown("[📺 YouTube](https://youtube.com/@WDPROFF) | [📸 Instagram](https://instagram.com/WDPROFF)")
    st.divider()
    user_key = st.text_input("🔑 API Key", value=api_key, type="password")

# --- 4. MAIN TABS ---
t1, t2, t3, t4 = st.tabs(["🎬 Captioner", "🎙️ AI Dubbing", "🚫 Watermark Remover", "🎨 Video Pro"])

# --- TAB 1: CAPTIONER (EXISTING LOGIC) ---
with t1:
    st.header("Ultra Hinglish Captioner")
    # Yahan wahi purana logic rahega jo humne last time banaya tha.

# --- TAB 2: AI DUBBING (NEW!) ---
with t2:
    st.header("🎙️ AI Video Dubbing")
    st.write("Video ki audio badlein (Hindi <-> English)")
    dub_video = st.file_uploader("Upload Video to Dub", type=["mp4"], key="dub")
    target_dub_lang = st.selectbox("Target Language", ["English", "Hindi"])
    
    if dub_video and st.button("🚀 Start Dubbing"):
        with st.spinner("AI is Dubbing... takes time!"):
            with tempfile.TemporaryDirectory() as tmp:
                v_in = os.path.join(tmp, "in.mp4")
                v_out = os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(dub_video.getbuffer())
                
                # 1. Speech to Text
                res = load_whisper().transcribe(v_in)
                full_text = res['text']
                
                # 2. Translate via Gemini
                genai.configure(api_key=user_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                t_prompt = f"Translate this video script to {target_dub_lang}. Maintain emotion. Script: {full_text}"
                translated_txt = model.generate_content(t_prompt).text
                
                # 3. Text to Speech (TTS)
                lang_code = 'en' if target_dub_lang == "English" else 'hi'
                tts = gTTS(translated_txt, lang=lang_code)
                tts_path = os.path.join(tmp, "dub.mp3")
                tts.save(tts_path)
                
                # 4. Merge Audio with Video
                video = VideoFileClip(v_in)
                new_audio = AudioFileClip(tts_path)
                final_v = video.set_audio(new_audio)
                final_v.write_videofile(v_out, codec="libx264", audio_codec="aac")
                
                st.video(v_out)

# --- TAB 3: WATERMARK REMOVER (NEW!) ---
with t3:
    st.header("🚫 Smart Watermark Remover")
    st.write("Video se watermark area ko blur karein.")
    wm_video = st.file_uploader("Upload Watermark Video", type=["mp4"], key="wm")
    col1, col2 = st.columns(2)
    wm_x = col1.number_input("Watermark X Position", 0, 2000, 50)
    wm_y = col2.number_input("Watermark Y Position", 0, 2000, 50)
    wm_w = col1.number_input("Watermark Width", 10, 500, 150)
    wm_h = col2.number_input("Watermark Height", 10, 500, 80)

    if wm_video and st.button("🚫 Remove Watermark"):
        with st.spinner("Blurring Watermark..."):
            with tempfile.TemporaryDirectory() as tmp:
                v_in = os.path.join(tmp, "in.mp4")
                v_out = os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(wm_video.getbuffer())
                
                cap = cv2.VideoCapture(v_in)
                fps = cap.get(cv2.CAP_PROP_FPS)
                fw, fh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (fw, fh))
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    # Watermark area blur logic
                    roi = frame[wm_y:wm_y+wm_h, wm_x:wm_x+wm_w]
                    roi = cv2.GaussianBlur(roi, (31, 31), 0)
                    frame[wm_y:wm_y+wm_h, wm_x:wm_x+wm_w] = roi
                    writer.write(frame)
                
                cap.release(); writer.release()
                st.success("Blur Applied!")
                # Sound merge and final output... (Logic similar to above)

# --- TAB 4: VIDEO PRO (4K & COLOR) ---
with t4:
    st.header("🎨 Video Pro (4K & Color Grading)")
    pro_video = st.file_uploader("Upload Video", type=["mp4"], key="pro")
    preset = st.selectbox("Choose Grade", ["Vibrant Gaming", "Cinematic Dark", "Cold Blue", "Warm Gold"])
    upscale = st.checkbox("Apply 4K Sharpening (Slow)")

    if pro_video and st.button("🔥 Apply Pro Effects"):
        # Yahan OpenCV se saturation badhane aur resize karne ka logic aayega.
        st.warning("4K processing is very heavy. Use small clips!")
    
