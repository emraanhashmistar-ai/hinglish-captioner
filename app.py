import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
import google.generativeai as genai
from gtts import gTTS

# --- 1. PREMIUM OFFICIAL UI & BRANDING ---
st.set_page_config(page_title="WD PRO FF - SUPREME", page_icon="🎬", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .main { background: #08090b; color: #e1e1e1; font-family: 'Segoe UI', sans-serif; }
    .welcome-header {
        text-align: center; font-size: 50px; font-weight: 900;
        background: linear-gradient(90deg, #ff0000, #ffffff, #ff0000);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: entrance 1.5s ease-out, glow 2s infinite alternate;
        margin-bottom: 20px;
    }
    @keyframes entrance { from { opacity:0; transform: translateY(-20px); } to { opacity:1; transform: translateY(0); } }
    @keyframes glow { from { filter: drop-shadow(0 0 10px #ff0000); } to { filter: drop-shadow(0 0 25px #ff0000); } }
    
    .stTabs [data-baseweb="tab-list"] { background: #121418; padding: 10px; border-radius: 12px; gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background: transparent; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px; color: #a0a0a0; font-weight: bold; transition: 0.3s; padding: 0 20px;
    }
    .stTabs [aria-selected="true"] { background: #ff0000 !important; color: white !important; border: none !important; box-shadow: 0 0 15px rgba(255,0,0,0.5); }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0000, #990000); color: white; border: none;
        border-radius: 10px; height: 3.5rem; font-size: 16px; font-weight: 800; transition: 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 6px 20px #ff0000; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 2. CORE ENGINES (Shared Functions) ---
@st.cache_resource
def load_whisper(): return whisper.load_model("base")

def get_pro_font(font_name, size):
    paths = {
        "Official Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Modern Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Classic Serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    }
    p = paths.get(font_name, paths["Official Bold"])
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def wrap_text(text, font, max_width):
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

# --- 3. SIDEBAR (WD PRO BRANDING) ---
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:red;'>WD PRO FF</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    st.markdown("### 🌐 OFFICIAL LINKS")
    st.markdown("[📺 YouTube: WD PRO FF](https://youtube.com/@WDPROFF)")
    st.markdown("[📸 Instagram: @WDPROFF](https://instagram.com/WDPROFF)")
    st.divider()
    user_key = st.text_input("🔑 API Key", value=api_key, type="password")

if 'app_started' not in st.session_state:
    st.balloons()
    st.markdown('<h1 class="welcome-header">WD PRO FF SUPREME 🔥</h1>', unsafe_allow_html=True)
    st.session_state.app_started = True

# --- 4. TABS SETUP ---
tab1, tab2, tab3, tab4 = st.tabs(["🎬 Ultra Captioner", "🎙️ AI Dubbing", "🚫 Watermark", "✨ Video Pro"])

# ==========================================
# TAB 1: ULTRA CAPTIONER (PROTECTED & DETAILED)
# ==========================================
with tab1:
    st.subheader("Official 50+ Style Captioning System")
    col1, col2 = st.columns(2)
    c_lang = col1.selectbox("Audio Language", ["Hinglish", "Hindi", "Urdu", "English", "Punjabi", "Arabic", "Spanish"])
    c_mode = col2.selectbox("Word Display Logic", ["1 Word (Fast)", "2 Words", "Full Sentence"])
    
    col3, col4 = st.columns(2)
    c_font = col3.selectbox("Font Style", ["Official Bold", "Modern Sans", "Classic Serif"])
    c_anim = col4.selectbox("Animation Style", ["Pop-Up", "Glow-Pulse", "Static"])
    
    c_size = st.slider("Caption Size", 20, 150, 70)
    c_color = st.color_picker("Text Color", "#FFFF00")
    c_outline = st.color_picker("Outline/Shadow Color", "#000000")
    c_pos = st.selectbox("Position", ["Bottom Center", "Middle", "Top Center"])
    
    c_vid = st.file_uploader("Upload Video for Captions", type=["mp4", "mov"], key="cap")
    
    if c_vid and st.button("🚀 GENERATE MASTER CAPTIONS"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(c_vid.getbuffer())
            
            # --- STEP 1: TRANSCRIBE ---
            st.info("🎙️ Hearing Audio via Whisper...")
            model_w = load_whisper()
            res = model_w.transcribe(v_in, language="hi" if c_lang == "Hinglish" else c_lang.lower()[:2])
            
            # --- STEP 2: ROMAN SCRIPT (HINGLISH) LOGIC ---
            st.info("✍️ Converting Script to Roman (Strictly No Translation)...")
            genai.configure(api_key=user_key)
            gemini = genai.GenerativeModel('gemini-1.5-flash')
            raw_input = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(res['segments'])])
            prompt = "TRANSLITERATE ONLY. DO NOT TRANSLATE. Convert to ROMAN SCRIPT (A-Z). JSON array only:\n" + raw_input
            
            try:
                ai_res = gemini.generate_content(prompt)
                h_list = json.loads(re.search(r'\[.*\]', ai_res.text, re.DOTALL).group())
                for i, s in enumerate(res['segments']):
                    # Safety check for KeyError and non-English chars
                    s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', h_list[i]) if i < len(h_list) else s['text']
            except Exception as e:
                # If AI fails, use original text so app DOES NOT crash
                for s in res['segments']: s["hinglish"] = s['text']

            # --- STEP 3: WORD-BY-WORD BREAKDOWN LOGIC ---
            final_segs = []
            words_per_seg = 1 if "1 Word" in c_mode else (2 if "2 Words" in c_mode else 999)
            
            for s in res['segments']:
                text_to_process = s.get("hinglish", s["text"])
                words = text_to_process.split()
                if not words: continue
                
                if words_per_seg == 999: # Full sentence
                    final_segs.append({'start': s['start'], 'end': s['end'], 'text': text_to_process})
                else:
                    duration = (s['end'] - s['start']) / len(words)
                    for i in range(0, len(words), words_per_seg):
                        chunk = " ".join(words[i:i+words_per_seg])
                        start_time = s['start'] + (i * duration)
                        end_time = s['start'] + ((i + words_per_seg) * duration)
                        final_segs.append({'start': start_time, 'end': end_time, 'text': chunk})

            # --- STEP 4: VIDEO RENDERING ---
            st.info("🎬 Rendering Captions onto Video (Syncing perfectly)...")
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
                    
                    # Micro-Animation Logic
                    current_size = c_size
                    if c_anim == "Pop-Up":
                        current_size = int(c_size * (1.15 if f_idx % 10 < 5 else 1.0))
                    elif c_anim == "Glow-Pulse":
                        current_size = int(c_size * (1.0 + 0.1 * np.sin(f_idx * 0.4)))
                    
                    font = get_pro_font(c_font, current_size)
                    
                    # Wrap Text Logic
                    max_w = w * 0.85
                    lines = wrap_text(txt, font, max_w)
                    total_h = len(lines) * (current_size + 10)
                    
                    # Position Logic
                    if "Bottom" in c_pos: start_y = h - total_h - 120
                    elif "Top" in c_pos: start_y = 120
                    else: start_y = (h - total_h) // 2

                    for i, line in enumerate(lines):
                        lw = font.getbbox(line)[2]
                        lx = (w - lw) // 2
                        ly = start_y + i * (current_size + 10)
                        
                        # Draw Outline/Shadow (Hardcoded 4px for solid look)
                        for ox in range(-3, 4):
                            for oy in range(-3, 4):
                                draw.text((lx+ox, ly+oy), line, font=font, fill=(or_, og, ob))
                        # Draw Main Text
                        draw.text((lx, ly), line, font=font, fill=(r, g, b))
                    
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
            cap.release(); writer.release()
            
            # --- STEP 5: MERGE AUDIO ---
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    final_clip = proc_vid.set_audio(orig_vid.audio)
                    final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ WD PRO CAPTION MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD CAPTIONED VIDEO", file, "wdpro_captions.mp4")

# ==========================================
# TAB 2: AI DUBBING (ERROR FIXED)
# ==========================================
with tab2:
    st.subheader("🎙️ AI Language Dubbing")
    st.write("Video ki aawaz ko dusri language mein naturally badlein.")
    d_target = st.selectbox("Translate Audio To", ["English", "Hindi"])
    d_vid = st.file_uploader("Upload Video", type=["mp4"], key="dub")
    
    if d_vid and st.button("🎙️ START DUBBING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(d_vid.getbuffer())
            
            st.info("1/3 Hearing original audio...")
            trans = load_whisper().transcribe(v_in)
            
            st.info("2/3 Translating script via Gemini AI...")
            genai.configure(api_key=user_key)
            # FIXED: Corrected Model Name to avoid NotFound Error
            model_g = genai.GenerativeModel('gemini-1.5-flash')
            translated_txt = model_g.generate_content(f"Translate this script strictly to {d_target}: {trans['text']}").text
            
            st.info("3/3 Generating New AI Voice & Merging...")
            lang_code = 'en' if d_target == "English" else 'hi'
            tts = gTTS(translated_txt, lang=lang_code)
            audio_path = os.path.join(tmp, "dub.mp3")
            tts.save(audio_path)
            
            # Merge New Audio with Original Video
            with VideoFileClip(v_in) as video:
                with AudioFileClip(audio_path) as new_audio:
                    # Clip audio to video duration just in case
                    final_video = video.set_audio(new_audio.set_duration(video.duration))
                    final_video.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ DUBBING COMPLETE!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD DUBBED VIDEO", file, "wdpro_dubbed.mp4")

# ==========================================
# TAB 3: WATERMARK REMOVER (BOUNDARIES FIXED)
# ==========================================
with tab3:
    st.subheader("🚫 Smart Area Blur")
    w_vid = st.file_uploader("Upload Video", type=["mp4"], key="wm")
    
    if w_vid:
        # Pre-read video to set STRICT slider limits (Fixes cv2.error)
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        t_file.write(w_vid.read())
        cap_temp = cv2.VideoCapture(t_file.name)
        v_width = int(cap_temp.get(cv2.CAP_PROP_FRAME_WIDTH))
        v_height = int(cap_temp.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_temp.release()
        
        st.write(f"Video Dimensions: {v_width}x{v_height}")
        col1, col2 = st.columns(2)
        wx = col1.slider("X Position (Start Left)", 0, v_width, int(v_width*0.1))
        wy = col2.slider("Y Position (Start Top)", 0, v_height, int(v_height*0.1))
        ww = col1.slider("Width of Blur", 10, v_width, 150)
        wh = col2.slider("Height of Blur", 10, v_height, 80)
        
        # Reset file pointer for processing
        w_vid.seek(0)
        
        if st.button("🚫 APPLY BLUR EFFECT"):
            with tempfile.TemporaryDirectory() as tmp:
                v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(w_vid.getbuffer())
                
                cap = cv2.VideoCapture(v_in)
                fps = cap.get(cv2.CAP_PROP_FPS)
                writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (v_width, v_height))
                
                st.info("Applying Gaussian Blur to selected region...")
                p_bar = st.progress(0)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                f_idx = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    # BOUNDARY PROTECTION (Prevents cv2.error crash)
                    x2 = min(wx + ww, v_width)
                    y2 = min(wy + wh, v_height)
                    
                    roi = frame[wy:y2, wx:x2]
                    if roi.size != 0: # Ensure valid region
                        frame[wy:y2, wx:x2] = cv2.GaussianBlur(roi, (51, 51), 0)
                        
                    writer.write(frame)
                    f_idx += 1
                    if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
                cap.release(); writer.release()
                
                # Merge original audio back
                with VideoFileClip(v_in) as orig_vid:
                    with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                        proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                
                st.success("✅ WATERMARK BLURRED!")
                st.video(v_out)
                with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD VIDEO", file, "wdpro_nologo.mp4")

# ==========================================
# TAB 4: VIDEO PRO ENHANCE (FULL LOGIC)
# ==========================================
with tab4:
    st.subheader("🎨 Professional Color Grading & Sharpening")
    p_vid = st.file_uploader("Upload Clip", type=["mp4"], key="pro")
    grade_preset = st.selectbox("Cinematic Preset", ["Vibrant Gaming (High Contrast/Sat)", "Cinematic Dark (Moody)", "Cool Blue (Sci-Fi)"])
    
    if p_vid and st.button("✨ APPLY ENHANCEMENTS"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(p_vid.getbuffer())
            
            st.info("Processing frames frame-by-frame (Takes time)...")
            cap = cv2.VideoCapture(v_in)
            fps, w, h = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            f_idx = 0
            p_bar = st.progress(0)
            
            # Sharpening Filter Kernel
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                # Apply Color Grading
                if grade_preset == "Vibrant Gaming (High Contrast/Sat)":
                    # Increase contrast and brightness slightly
                    frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
                    # Convert to HSV to boost saturation
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    hsv[:,:,1] = cv2.add(hsv[:,:,1], 30)
                    frame = cv2.cvtColor(hsv, cv2.HSV_BGR)
                
                elif grade_preset == "Cinematic Dark (Moody)":
                    # Decrease brightness, slightly increase contrast
                    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=-20)
                
                elif grade_preset == "Cool Blue (Sci-Fi)":
                    # Increase Blue channel
                    b, g, r = cv2.split(frame)
                    b = cv2.add(b, 20)
                    frame = cv2.merge((b, g, r))
                    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=0)

                # Apply Sharpening
                frame = cv2.filter2D(frame, -1, kernel_sharpen)
                
                writer.write(frame)
                f_idx += 1
                if f_idx % 20 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
            
            cap.release(); writer.release()
            
            # Merge original audio back
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ VIDEO ENHANCED & GRADED!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD ENHANCED VIDEO", file, "wdpro_enhanced
