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
from gtts import gTTS

# ==========================================
# 1. CINEMATIC & PROFESSIONAL UI
# ==========================================
st.set_page_config(page_title="WD PRO OFFICIAL", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    /* Sleek Dark Cinematic Theme */
    .main { background-color: #0d0d0d; color: #f2f2f2; font-family: 'Helvetica Neue', sans-serif; }
    
    /* WD PRO Premium Header */
    .wd-brand-title {
        text-align: center; font-size: 48px; font-weight: 900; letter-spacing: 4px;
        color: #ffffff; text-transform: uppercase; margin-bottom: 10px;
        text-shadow: 0px 4px 20px rgba(220, 20, 60, 0.6);
        animation: smoothFade 1.5s ease-in-out;
    }
    .wd-subtitle {
        text-align: center; font-size: 16px; color: #888888; letter-spacing: 2px;
        margin-bottom: 40px; text-transform: uppercase;
    }
    
    @keyframes smoothFade { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

    /* Elegant Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #141414; padding: 5px; border-radius: 8px; 
        border: 1px solid #222; justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; color: #666; font-weight: 600; font-size: 15px;
        border: none; transition: all 0.4s ease; padding: 10px 30px; border-radius: 5px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #dc143c !important; color: #ffffff !important; 
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.4);
    }
    
    /* Smooth Professional Buttons */
    .stButton>button {
        background-color: #1a1a1a; color: #ffffff; border: 1px solid #dc143c;
        border-radius: 6px; height: 3.2rem; font-size: 15px; font-weight: bold; letter-spacing: 1px;
        transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover { 
        background-color: #dc143c; border-color: #dc143c;
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(220, 20, 60, 0.5);
    }
    .stButton>button:active { transform: scale(0.98); }

    /* Sidebar Styling */
    .css-1d391kg { background-color: #0a0a0a; border-right: 1px solid #222; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINES
# ==========================================
@st.cache_resource
def load_whisper(): 
    return whisper.load_model("base")

def get_pro_font(font_name, size):
    paths = {
        "Cinematic Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Modern Clean": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Classic Serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    }
    p = paths.get(font_name, paths["Cinematic Bold"])
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def wrap_text_logic(text, font, max_width):
    words = text.split(); lines = []; current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        w = font.getbbox(test_line)[2]
        if w <= max_width: current_line.append(word)
        else:
            if current_line: lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: lines.append(" ".join(current_line))
    return lines

# ==========================================
# 3. SIDEBAR (WD PRO BRANDING)
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#ffffff; letter-spacing: 2px;'>WD PRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#dc143c; font-weight:bold;'>CREATOR STUDIO</p>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### OFFICIAL LINKS")
    st.markdown("[📺 WD PRO FF (YouTube)](https://youtube.com/@WDPROFF)")
    st.markdown("[📸 @WDPROFF (Instagram)](https://instagram.com/WDPROFF)")
    st.divider()
    user_key = st.text_input("API Key (System)", value=api_key, type="password")

# Header
st.markdown('<div class="wd-brand-title">WD PRO STUDIO</div>', unsafe_allow_html=True)
st.markdown('<div class="wd-subtitle">Professional Video Enhancement Suite</div>', unsafe_allow_html=True)

# ==========================================
# 4. TABBED WORKSPACE
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🎬 Auto Captions", "🎙️ AI Dubbing", "🚫 Smart Blur", "✨ Cinematic Color"])

# ==========================================
# TAB 1: CAPTIONER (PROTECTED)
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    c_lang = col1.selectbox("Audio Source", ["Hinglish", "Hindi", "Urdu", "English", "Punjabi"])
    c_mode = col2.selectbox("Word Display", ["1 Word (Fast)", "2 Words", "Full Sentence"])
    
    col3, col4 = st.columns(2)
    c_font = col3.selectbox("Font Style", ["Cinematic Bold", "Modern Clean", "Classic Serif"])
    c_anim = col4.selectbox("Text Effect", ["Smooth Fade", "Pop-Up", "Static"])
    
    col5, col6, col7 = st.columns(3)
    c_size = col5.slider("Text Size", 20, 150, 70)
    c_color = col6.color_picker("Text Color", "#FFFFFF")
    c_outline = col7.color_picker("Outline Color", "#000000")
    
    c_pos = st.selectbox("Vertical Position", ["Bottom", "Middle", "Top"])
    
    c_vid = st.file_uploader("Upload Video File", type=["mp4", "mov"], key="cap")
    
    if c_vid and st.button("PROCESS CAPTIONS"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(c_vid.getbuffer())
            
            st.info("Extracting and analyzing audio...")
            model_w = load_whisper()
            res = model_w.transcribe(v_in, language="hi" if c_lang == "Hinglish" else c_lang.lower()[:2])
            
            st.info("Generating Roman Script (Transliteration)...")
            genai.configure(api_key=user_key)
            gemini = genai.GenerativeModel('gemini-pro') # SAFE MODEL
            raw_input = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(res['segments'])])
            prompt = "TRANSLITERATE ONLY. NO TRANSLATION. Convert to ROMAN SCRIPT (A-Z). JSON array only:\n" + raw_input
            
            try:
                ai_res = gemini.generate_content(prompt)
                h_list = json.loads(re.search(r'\[.*\]', ai_res.text, re.DOTALL).group())
                for i, s in enumerate(res['segments']):
                    clean_text = h_list[i] if i < len(h_list) else s['text']
                    s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean_text)
            except Exception as e:
                for s in res['segments']: s["hinglish"] = s['text']

            # Word Breakdown
            final_segs = []
            words_per_seg = 1 if "1 Word" in c_mode else (2 if "2 Words" in c_mode else 999)
            
            for s in res['segments']:
                text_to_process = s.get("hinglish", s["text"])
                words = text_to_process.split()
                if not words: continue
                
                if words_per_seg == 999:
                    final_segs.append({'start': s['start'], 'end': s['end'], 'text': text_to_process})
                else:
                    duration = (s['end'] - s['start']) / len(words)
                    for i in range(0, len(words), words_per_seg):
                        chunk = " ".join(words[i:i+words_per_seg])
                        final_segs.append({'start': s['start'] + (i * duration), 'end': s['start'] + ((i + words_per_seg) * duration), 'text': chunk})

            st.info("Rendering visual elements...")
            cap = cv2.VideoCapture(v_in)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            r, g, b = int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16)
            or_, og, ob = int(c_outline[1:3],16), int(c_outline[3:5],16), int(c_outline[5:7],16)
            
            f_idx = 0
            p_bar = st.progress(0)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            while True:
                ret, frame = cap.read()
                if not ret: break
                
                curr_time = f_idx / fps
                txt = next((s['text'] for s in final_segs if s['start'] <= curr_time <= s['end']), "")
                
                if txt:
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(img)
                    
                    current_size = c_size
                    if c_anim == "Pop-Up": current_size = int(c_size * (1.1 if f_idx % 10 < 5 else 1.0))
                    
                    font = get_pro_font(c_font, current_size)
                    lines = wrap_text_logic(txt, font, w * 0.85)
                    total_h = len(lines) * (current_size + 10)
                    
                    if "Bottom" in c_pos: start_y = h - total_h - 100
                    elif "Top" in c_pos: start_y = 100
                    else: start_y = (h - total_h) // 2

                    for i, line in enumerate(lines):
                        lw = font.getbbox(line)[2]
                        lx = (w - lw) // 2
                        ly = start_y + i * (current_size + 10)
                        
                        for ox in range(-3, 4):
                            for oy in range(-3, 4):
                                draw.text((lx+ox, ly+oy), line, font=font, fill=(or_, og, ob))
                        draw.text((lx, ly), line, font=font, fill=(r, g, b))
                    
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
            cap.release(); writer.release()
            
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    final_clip = proc_vid.set_audio(orig_vid.audio)
                    final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("Rendering Complete!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("DOWNLOAD VIDEO", file, "wdpro_captions.mp4")

# ==========================================
# TAB 2: AI DUBBING (FIXED API ERROR)
# ==========================================
with tab2:
    d_target = st.selectbox("Translate Audio To", ["English", "Hindi"])
    d_vid = st.file_uploader("Upload Video File", type=["mp4"], key="dub")
    
    if d_vid and st.button("START DUBBING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(d_vid.getbuffer())
            
            st.info("Step 1: Extracting Audio...")
            trans = load_whisper().transcribe(v_in)
            
            st.info("Step 2: Translating Script...")
            genai.configure(api_key=user_key)
            try:
                # SAFE MODEL USED HERE
                model_g = genai.GenerativeModel('gemini-pro')
                ai_resp = model_g.generate_content(f"Translate this text to {d_target} directly. No intro, just translation: {trans['text']}")
                translated_txt = ai_resp.text
                
                st.info("Step 3: Generating Studio Voice...")
                lang_code = 'en' if d_target == "English" else 'hi'
                tts = gTTS(translated_txt, lang=lang_code)
                audio_path = os.path.join(tmp, "dub.mp3")
                tts.save(audio_path)
                
                with VideoFileClip(v_in) as video:
                    with AudioFileClip(audio_path) as new_audio:
                        final_video = video.set_audio(new_audio.set_duration(video.duration))
                        final_video.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("Dubbing Complete!")
                st.video(v_out)
                with open(v_out, "rb") as file: st.download_button("DOWNLOAD DUBBED VIDEO", file, "wdpro_dub.mp4")
            except Exception as e:
                st.error(f"API Error. Check Key or try again later. Details: {e}")

# ==========================================
# TAB 3: WATERMARK REMOVER
# ==========================================
with tab3:
    w_vid = st.file_uploader("Upload Target Video", type=["mp4"], key="wm")
    
    if w_vid:
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        t_file.write(w_vid.read())
        cap_temp = cv2.VideoCapture(t_file.name)
        v_width = int(cap_temp.get(cv2.CAP_PROP_FRAME_WIDTH))
        v_height = int(cap_temp.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_temp.release()
        
        col1, col2 = st.columns(2)
        wx = col1.slider("X Position", 0, v_width, int(v_width*0.1))
        wy = col2.slider("Y Position", 0, v_height, int(v_height*0.1))
        ww = col1.slider("Blur Width", 10, v_width, 150)
        wh = col2.slider("Blur Height", 10, v_height, 80)
        
        w_vid.seek(0)
        
        if st.button("APPLY SMART BLUR"):
            with tempfile.TemporaryDirectory() as tmp:
                v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(w_vid.getbuffer())
                
                cap = cv2.VideoCapture(v_in)
                fps = cap.get(cv2.CAP_PROP_FPS)
                writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (v_width, v_height))
                
                st.info("Applying blur effect to selected region...")
                p_bar = st.progress(0)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                f_idx = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    x2 = min(wx + ww, v_width)
                    y2 = min(wy + wh, v_height)
                    
                    roi = frame[wy:y2, wx:x2]
                    if roi.size != 0:
                        frame[wy:y2, wx:x2] = cv2.GaussianBlur(roi, (51, 51), 0)
                        
                    writer.write(frame)
                    f_idx += 1
                    if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
                cap.release(); writer.release()
                
                with VideoFileClip(v_in) as orig_vid:
                    with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                        proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("Watermark Masked!")
                st.video(v_out)
                with open(v_out, "rb") as file: st.download_button("DOWNLOAD VIDEO", file, "wdpro_clean.mp4")

# ==========================================
# TAB 4: VIDEO PRO (COLOR & SHARPNESS)
# ==========================================
with tab4:
    st.info("Note: True 4K upscaling requires powerful GPUs. This tool applies High-Definition Crisp Sharpening & Color Grading.")
    p_vid = st.file_uploader("Upload Clip", type=["mp4"], key="pro")
    grade_preset = st.selectbox("Cinematic LUTs", ["Vibrant Gaming (High Contrast)", "Cinematic Dark (Moody)", "Cool Tone"])
    
    if p_vid and st.button("ENHANCE VIDEO QUALITY"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(p_vid.getbuffer())
            
            st.info("Processing visual enhancements...")
            cap = cv2.VideoCapture(v_in)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            f_idx = 0
            p_bar = st.progress(0)
            
            # Crisp Sharpening Matrix
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                if grade_preset == "Vibrant Gaming (High Contrast)":
                    frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    hsv[:,:,1] = cv2.add(hsv[:,:,1], 30)
                    frame = cv2.cvtColor(hsv, cv2.HSV_BGR)
                elif grade_preset == "Cinematic Dark (Moody)":
                    frame = cv2.convertScaleAbs(frame, alpha=1.05, beta=-15)
                elif grade_preset == "Cool Tone":
                    b, g, r = cv2.split(frame)
                    b = cv2.add(b, 20)
                    frame = cv2.merge((b, g, r))
                    frame = cv2.convertScaleAbs(frame, alpha=1.05, beta=0)

                # Apply Crisp Sharpness
                frame = cv2.filter2D(frame, -1, kernel_sharpen)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 20 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
            
            cap.release(); writer.release()
            
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("Enhancement Complete!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("DOWNLOAD ENHANCED VIDEO", file, "wdpro_enhanced.mp4")
                
