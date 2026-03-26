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
# 1. PREMIUM OFFICIAL UI & BRANDING
# ==========================================
st.set_page_config(page_title="WD PRO FF - SUPREME ENGINE", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main { background: #050608; color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
    
    .welcome-header {
        text-align: center; font-size: 52px; font-weight: 900;
        background: linear-gradient(90deg, #ff0000, #ff7b00, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: dropIn 1.5s ease-out, glowPulse 2s infinite alternate;
        margin-bottom: 25px; text-transform: uppercase; letter-spacing: 2px;
    }
    @keyframes dropIn { from { opacity:0; transform: translateY(-30px); } to { opacity:1; transform: translateY(0); } }
    @keyframes glowPulse { from { filter: drop-shadow(0 0 10px #ff0000); } to { filter: drop-shadow(0 0 30px #ff0000); } }
    
    .stTabs [data-baseweb="tab-list"] { background: #0f1115; padding: 12px; border-radius: 15px; gap: 15px; border: 1px solid rgba(255,0,0,0.2); }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background: transparent; border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px; color: #888; font-weight: 700; font-size: 16px; transition: 0.4s; padding: 0 25px;
    }
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #ff0000, #aa0000) !important; 
        color: white !important; border: none !important; 
        box-shadow: 0 0 20px rgba(255,0,0,0.6); transform: scale(1.05);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0000, #880000); color: white; border: none;
        border-radius: 12px; height: 3.8rem; width: 100%; font-size: 18px; font-weight: 800; letter-spacing: 1px;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 5px 15px rgba(0,0,0,0.6);
    }
    .stButton>button:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(255,0,0,0.7); background: #ff1a1a; }
    .stButton>button:active { transform: scale(0.97); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINES (Shared Functions)
# ==========================================
@st.cache_resource
def load_whisper(): 
    return whisper.load_model("base")

def get_pro_font(font_name, size):
    paths = {
        "Official Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Modern Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Classic Serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    }
    p = paths.get(font_name, paths["Official Bold"])
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def wrap_text_logic(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        w = font.getbbox(test_line)[2]
        if w <= max_width: 
            current_line.append(word)
        else:
            if current_line: lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: lines.append(" ".join(current_line))
    return lines

# ==========================================
# 3. SIDEBAR (WD PRO OFFICIAL BRANDING)
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#ff0000; text-shadow: 0 0 10px red;'>WD PRO FF</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    st.markdown("### 🌐 OFFICIAL LINKS")
    st.markdown("""
    <div style="background:#111; padding:15px; border-radius:10px; border:1px solid red; text-align:center; margin-bottom:10px;">
        <a href="https://youtube.com/@WDPROFF" style="color:white; text-decoration:none; font-weight:bold; font-size:16px;">📺 YouTube: WD PRO FF</a>
    </div>
    <div style="background:#111; padding:15px; border-radius:10px; border:1px solid red; text-align:center; margin-bottom:15px;">
        <a href="https://instagram.com/WDPROFF" style="color:white; text-decoration:none; font-weight:bold; font-size:16px;">📸 Instagram: @WDPROFF</a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    user_key = st.text_input("🔑 System API Key", value=api_key, type="password")

if 'app_started' not in st.session_state:
    st.balloons()
    st.markdown('<h1 class="welcome-header">WD PRO FF SUPREME 🔥</h1>', unsafe_allow_html=True)
    st.session_state.app_started = True

# ==========================================
# 4. TABBED INTERFACE
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🎬 Ultra Captioner", "🎙️ AI Dubbing", "🚫 Watermark Pro", "✨ Video Pro"])

# ==========================================
# TAB 1: THE PERFECTED ULTRA CAPTIONER
# (Aapka ek bhi purana logic nahi hataya gaya hai)
# ==========================================
with tab1:
    st.markdown("### 🎬 Official 50+ Style Captioning System")
    
    col1, col2 = st.columns(2)
    c_lang = col1.selectbox("Audio Language", ["Hinglish", "Hindi", "Urdu", "English", "Punjabi", "Arabic", "Spanish"])
    c_mode = col2.selectbox("Word Display Logic", ["1 Word (Fast & Viral)", "2 Words", "Full Sentence"])
    
    col3, col4 = st.columns(2)
    c_font = col3.selectbox("Font Style", ["Official Bold", "Modern Sans", "Classic Serif"])
    c_anim = col4.selectbox("Animation Style", ["Pop-Up", "Glow-Pulse", "Shake", "Static"])
    
    col5, col6, col7 = st.columns(3)
    c_size = col5.slider("Caption Size", 20, 150, 75)
    c_color = col6.color_picker("Text Color", "#FFFF00")
    c_outline = col7.color_picker("Outline Color", "#000000")
    
    c_pos = st.selectbox("Position on Screen", ["Bottom Center", "Middle", "Top Center"])
    
    c_vid = st.file_uploader("Upload Video for Captions", type=["mp4", "mov"], key="cap")
    
    if c_vid and st.button("🚀 GENERATE MASTER CAPTIONS"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(c_vid.getbuffer())
            
            st.info("🎙️ Step 1/4: Hearing Audio perfectly...")
            model_w = load_whisper()
            res = model_w.transcribe(v_in, language="hi" if c_lang == "Hinglish" else c_lang.lower()[:2])
            
            st.info("✍️ Step 2/4: Converting to Roman Script (No Translation Rule Active)...")
            genai.configure(api_key=user_key)
            gemini = genai.GenerativeModel('gemini-1.5-flash')
            raw_input = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(res['segments'])])
            prompt = "STRICT RULE: TRANSLITERATE ONLY. DO NOT TRANSLATE. Convert to ROMAN SCRIPT (A-Z only). Example: 'Kaisa hai' remains 'Kaisa hai'. Return ONLY a valid JSON array of strings matching the input lines:\n" + raw_input
            
            try:
                ai_res = gemini.generate_content(prompt)
                h_list = json.loads(re.search(r'\[.*\]', ai_res.text, re.DOTALL).group())
                for i, s in enumerate(res['segments']):
                    clean_text = h_list[i] if i < len(h_list) else s['text']
                    s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean_text)
            except Exception as e:
                for s in res['segments']: s["hinglish"] = s['text']

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
                        start_time = s['start'] + (i * duration)
                        end_time = s['start'] + ((i + words_per_seg) * duration)
                        final_segs.append({'start': start_time, 'end': end_time, 'text': chunk})

            st.info("🎬 Step 3/4: Rendering 3D Animations & Syncing Captions...")
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
                    offset_x, offset_y = 0, 0
                    
                    if c_anim == "Pop-Up":
                        current_size = int(c_size * (1.15 if f_idx % 10 < 5 else 1.0))
                    elif c_anim == "Glow-Pulse":
                        current_size = int(c_size * (1.0 + 0.1 * np.sin(f_idx * 0.4)))
                    elif c_anim == "Shake":
                        offset_x = int(5 * np.sin(f_idx * 0.8))
                    
                    font = get_pro_font(c_font, current_size)
                    
                    max_w = w * 0.85
                    lines = wrap_text_logic(txt, font, max_w)
                    total_h = len(lines) * (current_size + 10)
                    
                    if "Bottom" in c_pos: start_y = h - total_h - 130
                    elif "Top" in c_pos: start_y = 130
                    else: start_y = (h - total_h) // 2

                    for i, line in enumerate(lines):
                        lw = font.getbbox(line)[2]
                        lx = ((w - lw) // 2) + offset_x
                        ly = start_y + i * (current_size + 10) + offset_y
                        
                        for ox in range(-4, 5):
                            for oy in range(-4, 5):
                                draw.text((lx+ox, ly+oy), line, font=font, fill=(or_, og, ob))
                        draw.text((lx, ly), line, font=font, fill=(r, g, b))
                    
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
            cap.release(); writer.release()
            
            st.info("🔊 Step 4/4: Merging Original Audio...")
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    final_clip = proc_vid.set_audio(orig_vid.audio)
                    final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ WD PRO CAPTION MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD YOUR VIDEO", file, "wdpro_captions.mp4")

# ==========================================
# TAB 2: AI DUBBING
# ==========================================
with tab2:
    st.markdown("### 🎙️ AI Language Dubbing")
    d_target = st.selectbox("Translate Audio To", ["English", "Hindi"])
    d_vid = st.file_uploader("Upload Video", type=["mp4"], key="dub")
    
    if d_vid and st.button("🎙️ START DUBBING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(d_vid.getbuffer())
            
            st.info("Hearing original audio...")
            trans = load_whisper().transcribe(v_in)
            
            st.info("Translating script via AI...")
            genai.configure(api_key=user_key)
            model_g = genai.GenerativeModel('gemini-1.5-flash')
            translated_txt = model_g.generate_content(f"Translate this script strictly to {d_target}: {trans['text']}").text
            
            st.info("Generating AI Voice & Merging...")
            lang_code = 'en' if d_target == "English" else 'hi'
            tts = gTTS(translated_txt, lang=lang_code)
            audio_path = os.path.join(tmp, "dub.mp3")
            tts.save(audio_path)
            
            with VideoFileClip(v_in) as video:
                with AudioFileClip(audio_path) as new_audio:
                    final_video = video.set_audio(new_audio.set_duration(video.duration))
                    final_video.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ DUBBING COMPLETE!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD DUBBED VIDEO", file, "wdpro_dubbed.mp4")

# ==========================================
# TAB 3: WATERMARK REMOVER
# ==========================================
with tab3:
    st.markdown("### 🚫 Smart Area Blur (Watermark Remover)")
    w_vid = st.file_uploader("Upload Video", type=["mp4"], key="wm")
    
    if w_vid:
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        t_file.write(w_vid.read())
        cap_temp = cv2.VideoCapture(t_file.name)
        v_width = int(cap_temp.get(cv2.CAP_PROP_FRAME_WIDTH))
        v_height = int(cap_temp.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_temp.release()
        
        col1, col2 = st.columns(2)
        wx = col1.slider("X Position (Left to Right)", 0, v_width, int(v_width*0.1))
        wy = col2.slider("Y Position (Top to Bottom)", 0, v_height, int(v_height*0.1))
        ww = col1.slider("Width of Blur Area", 10, v_width, 150)
        wh = col2.slider("Height of Blur Area", 10, v_height, 80)
        
        w_vid.seek(0)
        
        if st.button("🚫 APPLY BLUR EFFECT"):
            with tempfile.TemporaryDirectory() as tmp:
                v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(w_vid.getbuffer())
                
                cap = cv2.VideoCapture(v_in)
                fps = cap.get(cv2.CAP_PROP_FPS)
                writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (v_width, v_height))
                
                st.info("Processing frames to blur selected area...")
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
                        frame[wy:y2, wx:x2] = cv2.GaussianBlur(roi, (61, 61), 0)
                        
                    writer.write(frame)
                    f_idx += 1
                    if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
                cap.release(); writer.release()
                
                with VideoFileClip(v_in) as orig_vid:
                    with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                        proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ WATERMARK BLURRED SUCCESSFULLY!")
                st.video(v_out)
                with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD VIDEO", file, "wdpro_nologo.mp4")

# ==========================================
# TAB 4: VIDEO PRO ENHANCE (ERROR FIXED HERE)
# ==========================================
with tab4:
    st.markdown("### 🎨 Professional Color Grading")
    p_vid = st.file_uploader("Upload Clip", type=["mp4"], key="pro")
    grade_preset = st.selectbox("Cinematic Preset", ["Vibrant Gaming (High Contrast/Sat)", "Cinematic Dark (Moody)", "Cool Blue (Sci-Fi)"])
    
    if p_vid and st.button("✨ APPLY ENHANCEMENTS"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(p_vid.getbuffer())
            
            st.info("Enhancing colors and sharpening details...")
            cap = cv2.VideoCapture(v_in)
            fps, w, h = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            f_idx = 0
            p_bar = st.progress(0)
            
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                if grade_preset == "Vibrant Gaming (High Contrast/Sat)":
                    frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    hsv[:,:,1] = cv2.add(hsv[:,:,1], 30)
                    # YAHAN ERROR THA JO MENE THEEK KIYA HAI (cv2.COLOR_HSV2BGR)
                    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                elif grade_preset == "Cinematic Dark (Moody)":
                    frame = cv2.convertScaleAbs(frame, alpha=1.05, beta=-20)
                elif grade_preset == "Cool Blue (Sci-Fi)":
                    b, g, r = cv2.split(frame)
                    b = cv2.add(b, 20)
                    frame = cv2.merge((b, g, r))
                    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=0)

                frame = cv2.filter2D(frame, -1, kernel_sharpen)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 20 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
            
            cap.release(); writer.release()
            
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ VIDEO ENHANCED & GRADED!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD ENHANCED VIDEO", file, "wdpro_enhanced.mp4")
        
