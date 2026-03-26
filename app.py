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

# --- 1. PRO GAMING UI ---
st.set_page_config(page_title="WD PRO FF - SUPREME ENGINE", page_icon="🎮", layout="wide")

st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a0000 0%, #020202 100%); color: white; }
    .stButton>button { 
        background: linear-gradient(135deg, #ff0000, #440000); 
        color: white; border-radius: 12px; font-weight: bold; border: 2px solid #ff4b4b; 
        height: 4rem; width: 100%; transition: 0.3s; box-shadow: 0 0 15px rgba(255, 0, 0, 0.4);
    }
    .stButton>button:hover { box-shadow: 0 0 35px #ff0000; transform: translateY(-3px); }
    .social-btn { 
        text-decoration: none; color: #ffd700; background: #111; display: block; padding: 12px; 
        border-radius: 10px; text-align: center; margin-bottom: 10px; border: 1px solid #ff0000;
        font-weight: bold; transition: 0.3s;
    }
    .social-btn:hover { background: #ff0000; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC FUNCTIONS ---
@st.cache_resource
def load_whisper(): return whisper.load_model("base")

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        w = font.getbbox(test_line)[2]
        if w <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    return lines

def get_font(font_name, size):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if font_name == "Gaming Bold": path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    elif font_name == "Serif": path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()

# --- 3. SIDEBAR (WD PRO FF BRANDING) ---
saved_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:red;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/free-fire.png")
    
    st.markdown("### 🔗 SOCIAL LINKS")
    st.markdown('<a href="https://youtube.com/@WDPROFF" target="_blank" class="social-btn">📺 YouTube: WD PRO FF</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/WDPROFF" target="_blank" class="social-btn">📸 Instagram: @WDPROFF</a>', unsafe_allow_html=True)
    
    st.divider()
    api_key = st.text_input("🔑 Gemini API Key", value=saved_key, type="password")
    
    st.header("🎨 CAPTION STYLE")
    display_mode = st.selectbox("Display Mode", ["Full Sentence", "Word-by-Word (Fast)", "2 Words at a Time"])
    f_style = st.selectbox("Font Style", ["Gaming Bold", "Sans Modern", "Serif Pro", "Classic"])
    f_anim = st.selectbox("Animation", ["Pop-Up", "Glow Pulse", "Fade In", "Static"])
    f_pos = st.selectbox("Position", ["Bottom Center", "Middle Center", "Top Center"])
    
    st.header("🖌️ APPEARANCE")
    f_size = st.slider("Text Size", 20, 180, 70)
    t_color = st.color_picker("Text Color", "#FFFF00")
    outline_color = st.color_picker("Outline Color", "#000000")
    outline_width = st.slider("Outline Thickness", 0, 10, 4)

# --- 4. HINGLISH LOGIC (STRICT ROMAN) ---
def transliterate(segments, key):
    if not segments or not key: return segments
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    raw = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(segments)])
    prompt = "STRICT: Convert to ROMAN SCRIPT (English Alphabet). NO Translation. If input is 'Udhar jao', output 'Udhar jao'. JSON array only:\n" + raw
    try:
        res = model.generate_content(prompt)
        h_list = json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
        for i, s in enumerate(segments):
            clean = h_list[i] if i < len(h_list) else s['text']
            s["hinglish"] = re.sub(r'[^\x00-\x7F]+', '', clean)
    except: pass
    return segments

# --- 5. RENDER ENGINE (WORD-BY-WORD & WRAPPING) ---
def render_video(v_in, segments, v_out, f_size, t_color, o_color, o_width, pos, mode, anim, font_name):
    cap = cv2.VideoCapture(v_in)
    fps, w, h = cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_v = v_out + "_temp.mp4"
    writer = cv2.VideoWriter(temp_v, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    
    # Process Word-by-Word if selected
    final_segments = []
    if mode != "Full Sentence":
        words_per_seg = 1 if "Word-by-Word" in mode else 2
        for s in segments:
            words = s['hinglish'].split()
            duration = (s['end'] - s['start']) / max(len(words), 1)
            for i in range(0, len(words), words_per_seg):
                chunk = " ".join(words[i:i+words_per_seg])
                final_segments.append({
                    'start': s['start'] + (i//words_per_seg) * duration,
                    'end': s['start'] + (i//words_per_seg + 1) * duration,
                    'text': chunk
                })
    else:
        for s in segments: final_segments.append({'start': s['start'], 'end': s['end'], 'text': s['hinglish']})

    f_idx = 0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    p_bar = st.progress(0)
    
    r,g,b = int(t_color[1:3],16), int(t_color[3:5],16), int(t_color[5:7],16)
    or_,og,ob = int(o_color[1:3],16), int(o_color[3:5],16), int(o_color[5:7],16)

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        curr_t = f_idx / fps
        txt = next((s['text'] for s in final_segments if s['start'] <= curr_t <= s['end']), "")
        
        if txt:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            
            # Animation Logic
            s_size = f_size
            if anim == "Pop-Up": s_size = int(f_size * (1.1 if (f_idx % 10 < 5) else 1.0))
            elif anim == "Glow Pulse": s_size = int(f_size * (1.0 + 0.1 * np.sin(f_idx * 0.5)))
            
            font = get_font(font_name, s_size)
            lines = wrap_text(txt, font, w * 0.8) # Wrap at 80% screen width
            
            # Calculate total height of all lines
            total_h = len(lines) * (s_size + 10)
            
            # Position Logic
            if "Bottom" in pos: start_y = h - total_h - 120
            elif "Top" in pos: start_y = 120
            else: start_y = (h - total_h) // 2

            for i, line in enumerate(lines):
                lw = font.getbbox(line)[2]
                lx = (w - lw) // 2
                ly = start_y + i * (s_size + 10)
                
                # Outline
                if o_width > 0:
                    for ox in range(-o_width, o_width+1):
                        for oy in range(-o_width, o_width+1):
                            draw.text((lx+ox, ly+oy), line, font=font, fill=(or_,og,ob))
                
                draw.text((lx, ly), line, font=font, fill=(r,g,b))
            
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
        writer.write(frame); f_idx += 1
        if f_idx % 30 == 0: p_bar.progress(min(f_idx/total_f, 1.0))
        
    cap.release(); writer.release()
    with VideoFileClip(v_in) as orig:
        with VideoFileClip(temp_v) as proc:
            proc.set_audio(orig.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)

# --- 6. MAIN APP FLOW ---
st.markdown("<h2 style='text-align:center;'>🚀 WD PRO ULTRA CAPTIONER</h2>", unsafe_allow_html=True)
up = st.file_uploader("Upload Game Video", type=["mp4"])

if up and api_key:
    if st.button("🔥 GENERATE MAGIC"):
        with tempfile.TemporaryDirectory() as tmp:
            v_in, v_out = os.path.join(tmp, "i.mp4"), os.path.join(tmp, "o.mp4")
            with open(v_in, "wb") as f: f.write(up.getbuffer())
            
            st.info("🎙️ Hearing Audio...")
            model = load_whisper()
            res = model.transcribe(v_in)
            
            st.info("✍️ Transliterating to Roman Script...")
            segs = transliterate(res['segments'], api_key)
            
            st.info("🎬 Rendering with Pro Effects...")
            render_video(v_in, segs, v_out, f_size, t_color, outline_color, outline_width, pos, display_mode, f_anim, f_style)
            
            st.success("🏆 WD PRO FF STYLE READY!")
            st.video(v_out)
            with open(v_out, "rb") as f: st.download_button("📥 DOWNLOAD", f, "wd_pro_video.mp4")
    
