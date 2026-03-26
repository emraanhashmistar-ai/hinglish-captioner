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
# 1. PREMIUM OFFICIAL UI & WELCOME ANIMATION
# ==========================================
st.set_page_config(page_title="WD PRO FF - STUDIO", page_icon="🎬", layout="wide")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    /* Ultra-Premium Dark Theme */
    .main { background-color: #030406; color: #f0f0f0; font-family: 'Inter', sans-serif; }
    
    /* Permanent Welcome Animation */
    .wd-welcome {
        text-align: center; font-size: 50px; font-weight: 900;
        background: linear-gradient(90deg, #ff0000, #ff4040, #ff0000);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: dropDown 1s cubic-bezier(0.25, 1, 0.5, 1), shine 3s linear infinite;
        margin-top: 20px; margin-bottom: 30px; letter-spacing: 3px;
        text-shadow: 0px 5px 15px rgba(255, 0, 0, 0.3);
    }
    @keyframes dropDown { from { opacity: 0; transform: translateY(-40px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes shine { to { background-position: 200% center; } }
    
    /* Pro Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #0b0c10; padding: 10px; border-radius: 12px; gap: 10px; border: 1px solid #1f1f1f; }
    .stTabs [data-baseweb="tab"] {
        height: 48px; background: transparent; border: 1px solid transparent;
        border-radius: 8px; color: #777; font-weight: 700; font-size: 16px; transition: 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #e60000, #990000) !important; 
        color: white !important; box-shadow: 0 4px 15px rgba(230,0,0,0.5); border: 1px solid #ff1a1a !important;
    }
    
    /* Smooth Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #e60000, #a30000); color: white; border: none;
        border-radius: 8px; height: 3.5rem; width: 100%; font-size: 16px; font-weight: 800; letter-spacing: 1px;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(230,0,0,0.6); background: #ff0000; }
    .stButton>button:active { transform: scale(0.97); }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            document.getElementById('clickSound').play();
        }
    });
    </script>
""", unsafe_allow_html=True)

# Main Welcome Banner (Always plays on load)
st.markdown('<div class="wd-welcome">WD PRO FF SUPREME 🔥</div>', unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINES
# ==========================================
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

def wrap_text_logic(text, font, max_width):
    words = text.split(); lines = []; current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        if font.getbbox(test_line)[2] <= max_width: current_line.append(word)
        else:
            if current_line: lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: lines.append(" ".join(current_line))
    return lines

# Color Grading Logic (New & Perfected)
def apply_color_grade(frame, bright, cont, sat, warmth):
    # Contrast and Brightness
    frame = cv2.convertScaleAbs(frame, alpha=cont, beta=bright)
    
    # Saturation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = hsv[:, :, 1] * sat
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    # Warmth (Red/Blue balance)
    if warmth != 0:
        b, g, r = cv2.split(frame.astype(np.int16))
        r = np.clip(r + warmth, 0, 255)
        b = np.clip(b - warmth, 0, 255)
        frame = cv2.merge((b, g, r)).astype(np.uint8)
    
    return frame

# ==========================================
# 3. SIDEBAR BRANDING
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#e60000; text-shadow: 0 0 10px rgba(230,0,0,0.5);'>WD PRO FF</h2>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    st.markdown("### 🌐 OFFICIAL LINKS")
    st.markdown("""
    <div style="background:#111; padding:12px; border-radius:8px; border:1px solid #e60000; text-align:center; margin-bottom:10px;">
        <a href="https://youtube.com/@WDPROFF" style="color:white; text-decoration:none; font-weight:bold;">📺 YouTube: WD PRO</a>
    </div>
    <div style="background:#111; padding:12px; border-radius:8px; border:1px solid #e60000; text-align:center; margin-bottom:15px;">
        <a href="https://instagram.com/WDPROFF" style="color:white; text-decoration:none; font-weight:bold;">📸 Instagram: @WDPROFF</a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    user_key = st.text_input("🔑 API Key", value=api_key, type="password")

# ==========================================
# 4. TABS SETUP
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🎬 Ultra Captioner", "🎙️ AI Dubbing", "🚫 Watermark Pro", "✨ Cinematic Color Pro"])

# ==========================================
# TAB 1: ULTRA CAPTIONER (PERFECT & UNTOUCHED)
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    c_lang = col1.selectbox("Audio Language", ["Hinglish", "Hindi", "Urdu", "English", "Punjabi", "Arabic"])
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
            
            st.info("✍️ Step 2/4: Converting to Roman Script (No Translation Rule)...")
            genai.configure(api_key=user_key)
            gemini = genai.GenerativeModel('gemini-1.5-flash')
            raw_input = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(res['segments'])])
            prompt = "STRICT RULE: TRANSLITERATE ONLY. DO NOT TRANSLATE. Convert to ROMAN SCRIPT (A-Z only). Return JSON array:\n" + raw_input
            
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
                        final_segs.append({'start': s['start'] + (i * duration), 'end': s['start'] + ((i + words_per_seg) * duration), 'text': chunk})

            st.info("🎬 Step 3/4: Rendering 3D Animations & Syncing Captions...")
            cap = cv2.VideoCapture(v_in)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            r, g, b = int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16)
            or_, og, ob = int(c_outline[1:3],16), int(c_outline[3:5],16), int(c_outline[5:7],16)
            
            f_idx = 0; p_bar = st.progress(0); total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            while True:
                ret, frame = cap.read()
                if not ret: break
                
                curr_time = f_idx / fps
                txt = next((s['text'] for s in final_segs if s['start'] <= curr_time <= s['end']), "")
                
                if txt:
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(img)
                    
                    current_size = c_size; offset_x = 0
                    if c_anim == "Pop-Up": current_size = int(c_size * (1.15 if f_idx % 10 < 5 else 1.0))
                    elif c_anim == "Glow-Pulse": current_size = int(c_size * (1.0 + 0.1 * np.sin(f_idx * 0.4)))
                    elif c_anim == "Shake": offset_x = int(5 * np.sin(f_idx * 0.8))
                    
                    font = get_pro_font(c_font, current_size)
                    lines = wrap_text_logic(txt, font, w * 0.85)
                    total_h = len(lines) * (current_size + 10)
                    
                    if "Bottom" in c_pos: start_y = h - total_h - 130
                    elif "Top" in c_pos: start_y = 130
                    else: start_y = (h - total_h) // 2

                    for i, line in enumerate(lines):
                        lw = font.getbbox(line)[2]
                        lx = ((w - lw) // 2) + offset_x
                        ly = start_y + i * (current_size + 10)
                        
                        for ox in range(-4, 5):
                            for oy in range(-4, 5): draw.text((lx+ox, ly+oy), line, font=font, fill=(or_, og, ob))
                        draw.text((lx, ly), line, font=font, fill=(r, g, b))
                    
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                writer.write(frame); f_idx += 1
                if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
            cap.release(); writer.release()
            
            st.info("🔊 Step 4/4: Merging Original Audio...")
            with VideoFileClip(v_in) as orig_vid:
                with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                    final_clip = proc_vid.set_audio(orig_vid.audio)
                    final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ WD PRO CAPTION MASTERPIECE READY!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD CAPTIONED VIDEO", file, "wdpro_captions.mp4")

# ==========================================
# TAB 2: AI DUBBING (TOTALLY REBUILT & FIXED)
# ==========================================
with tab2:
    st.markdown("### 🎙️ AI Voice Dubbing Engine")
    d_target = st.selectbox("Translate Audio To", ["English", "Hindi"])
    d_vid = st.file_uploader("Upload Video", type=["mp4"], key="dub")
    
    if d_vid and st.button("🎙️ START DUBBING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(d_vid.getbuffer())
            
            st.info("1/3 Hearing original audio...")
            trans = load_whisper().transcribe(v_in)
            
            st.info("2/3 Translating script via AI...")
            genai.configure(api_key=user_key)
            try:
                model_g = genai.GenerativeModel('gemini-1.5-flash')
                ai_resp = model_g.generate_content(f"Translate this text to {d_target}. Only give the translation, nothing else: {trans['text']}")
                translated_txt = ai_resp.text.strip()
                if not translated_txt: translated_txt = "Sorry, translation failed."
            except Exception as e:
                translated_txt = "API Error occurred during translation."
            
            st.info("3/3 Generating AI Voice & Merging...")
            lang_code = 'en' if d_target == "English" else 'hi'
            tts = gTTS(translated_txt, lang=lang_code)
            audio_path = os.path.join(tmp, "dub.mp3")
            tts.save(audio_path)
            
            # Merging Audio and Video carefully
            with VideoFileClip(v_in) as video:
                with AudioFileClip(audio_path) as new_audio:
                    # Sync logic to prevent crash
                    final_video = video.set_audio(new_audio)
                    final_video.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("✅ DUBBING COMPLETE!")
            st.video(v_out)
            with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD DUBBED VIDEO", file, "wdpro_dubbed.mp4")

# ==========================================
# TAB 3: WATERMARK REMOVER (UNTOUCHED & SAFE)
# ==========================================
with tab3:
    st.markdown("### 🚫 Smart Area Blur")
    w_vid = st.file_uploader("Upload Video", type=["mp4"], key="wm")
    
    if w_vid:
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        t_file.write(w_vid.read())
        cap_temp = cv2.VideoCapture(t_file.name)
        v_width, v_height = int(cap_temp.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_temp.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_temp.release()
        
        col1, col2 = st.columns(2)
        wx = col1.slider("X Position (Left to Right)", 0, v_width, int(v_width*0.1))
        wy = col2.slider("Y Position (Top to Bottom)", 0, v_height, int(v_height*0.1))
        ww = col1.slider("Width of Blur", 10, v_width, 150)
        wh = col2.slider("Height of Blur", 10, v_height, 80)
        w_vid.seek(0)
        
        if st.button("🚫 APPLY BLUR EFFECT"):
            with tempfile.TemporaryDirectory() as tmp:
                v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
                with open(v_in, "wb") as f: f.write(w_vid.getbuffer())
                
                cap = cv2.VideoCapture(v_in)
                fps = cap.get(cv2.CAP_PROP_FPS)
                writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (v_width, v_height))
                
                st.info("Processing frames...")
                p_bar = st.progress(0); total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); f_idx = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    x2, y2 = min(wx + ww, v_width), min(wy + wh, v_height)
                    roi = frame[wy:y2, wx:x2]
                    if roi.size != 0: frame[wy:y2, wx:x2] = cv2.GaussianBlur(roi, (61, 61), 0)
                        
                    writer.write(frame); f_idx += 1
                    if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_frames, 1.0))
                
                cap.release(); writer.release()
                
                with VideoFileClip(v_in) as orig_vid:
                    with VideoFileClip(v_out + "_tmp.mp4") as proc_vid:
                        proc_vid.set_audio(orig_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                st.success("✅ WATERMARK BLURRED!")
                st.video(v_out)
                with open(v_out, "rb") as file: st.download_button("📥 DOWNLOAD CLEAN VIDEO", file, "wdpro_clean.mp4")

# ==========================================
# TAB 4: CINEMATIC COLOR PRO (TOTALLY NEW & MANUAL)
# ==========================================
with tab4:
    st.markdown("### ✨ Cinematic Color & Grade")
    st.write("Ab hazze aur kharab color nahi! Perfect smooth grading.")
    
    p_vid = st.file_uploader("Upload Clip", type=["mp4"], key="pro")
    
    mode = st.radio("Grading Mode", ["🤖 AI Recommended Presets", "🎛️ Manual Pro Control"], horizontal=True)
    
    if mode == "🤖 AI Recommended Presets":
        presets = {
            "Cinematic Teal & Orange": {"b": 5, "c": 1.1, "s": 1.2, "w": 10},
            "Vibrant Gaming (HD Pop)": {"b": 10, "c": 1.15, "s": 1.4, "w": 5},
            "Moody Dark (Sad/Attitude)": {"b": -15, "c": 1.05, "s": 0.8, "w": -5},
            "Cold Sci-Fi (Blue Tone)": {"b": 0, "c": 1.1, "s": 1.0, "w": -20},
            "Warm Vintage (Sunset)": {"b": 5, "c": 1.0, "s": 1.1, "w": 25}
        }
        sel_preset = st.selectbox("Choose AI Cinematic Filter", list(presets.keys()))
        b_val = presets[sel_preset]["b"]
        c_val = presets[sel_preset]["c"]
        s_val = presets[sel_preset]["s"]
        w_val = presets[sel_preset]["w"]
        
    else:
        st.markdown("#### Manual Adjustments")
        colA, colB = st.columns(2)
        b_val = colA.slider("Brightness", -50, 50, 0)
        c_val = colB.slider("Contrast", 0.5, 1.5, 1.0)
        s_val = colA.slider("Saturation (Color Pop)", 0.0, 2.0, 1.0)
        w_val = colB.slider("Warmth (Red/Blue)", -50, 50, 0)
    
    sharp_check = st.checkbox("Apply Cinematic Soft Sharpening (No Haze)", value=True)
    
    if p_vid and st.button("✨ APPLY COLOR GRADING"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "in.mp4"), os.path.join(tmp, "out.mp4")
            with open(v_in, "wb") as f: f.write(p_vid.getbuffer())
            
            st.info("Enhancing video frame-by-frame smoothly...")
            cap = cv2.VideoCapture(v_in)
            fps, w, h = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_tmp.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            f_idx = 0; p_bar = st.progress(0)
            
            while True:
                ret,
