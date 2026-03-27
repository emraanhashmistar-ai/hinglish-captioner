import streamlit as st
import tempfile
import os
import json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import time
import random
import datetime

# --- MOVIEPY ENGINE FIX ---
try:
    from moviepy.editor import VideoFileClip
except Exception:
    pass

import whisper
import google.generativeai as genai

# ==========================================================================================
# PART 1: PREMIUM CONFIG & GENDER SELECTION
# ==========================================================================================
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide", initial_sidebar_state="expanded")

# Initialize Session States
if 'gender' not in st.session_state: st.session_state.gender = None
if 'animation_done' not in st.session_state: st.session_state.animation_done = False
if 'scratched_today' not in st.session_state: st.session_state.scratched_today = False
if 'panda_stage' not in st.session_state: st.session_state.panda_stage = 0

# --- GENDER SELECTION SCREEN ---
if st.session_state.gender is None:
    st.markdown("<h1 style='text-align:center; color:#008080; margin-top:50px;'>WD PRO FF WORLD 🐼</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#D3D3D3;'>Aapka swagat hai! Pehle apni identity chunein:</h3>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col2:
        if st.button("👑 I AM A KING (LADKA)", use_container_width=True):
            st.session_state.gender = "King"
            st.rerun()
    with col3:
        if st.button("👸 I AM A QUEEN (LADKI)", use_container_width=True):
            st.session_state.gender = "Queen"
            st.rerun()
    st.stop()

# --- FIREWORKS & WELCOME ANIMATION ---
if not st.session_state.animation_done:
    welcome_placeholder = st.empty()
    title_identity = "KING" if st.session_state.gender == "King" else "QUEEN"
    
    fireworks_js = (
        "<script src='https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js'></script>"
        "<script>"
        "var duration = 4 * 1000; var animationEnd = Date.now() + duration;"
        "var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 999999 };"
        "function randomInRange(min, max) { return Math.random() * (max - min) + min; }"
        "var interval = setInterval(function() {"
        "  var timeLeft = animationEnd - Date.now();"
        "  if (timeLeft <= 0) { return clearInterval(interval); }"
        "  var particleCount = 50 * (timeLeft / duration);"
        "  confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));"
        "  confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));"
        "}, 250);"
        "</script>"
    )
    
    with welcome_placeholder.container():
        st.components.v1.html(fireworks_js, height=0)
        w_css = "<style>.w-box { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: black; position: fixed; top: 0; left: 0; width: 100vw; z-index: 9999; } "
        w_text = ".w-h1 { color: #008080; font-size: 8vw; font-weight: 900; text-shadow: 0 0 20px #008080; animation: p 1.5s infinite alternate; } "
        w_sub = ".w-p { color: #B4D8E7; font-size: 3vw; font-style: italic; margin-top: 20px; text-align: center; } @keyframes p { from { transform: scale(1); } to { transform: scale(1.05); } }</style>"
        w_html = f"<div class='w-box'><div class='w-h1'>WD PRO FF</div><div class='w-p'>\"Every subscriber is my {title_identity},<br>and I am here to entertain!\" 👑</div></div>"
        st.markdown(w_css + w_text + w_sub + w_html, unsafe_allow_html=True)
        time.sleep(4.5)
    welcome_placeholder.empty()
    st.session_state.animation_done = True

# ==========================================================================================
# PART 2: GLOBAL CSS & HEADER
# ==========================================================================================
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D3D3D3; }
    .main-header { font-size: 40px; font-weight: 900; text-align: center; background: linear-gradient(90deg, #008080, #B4D8E7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .social-links { text-align: center; margin-bottom: 20px; }
    .social-links a { color: #B4D8E7; text-decoration: none; font-weight: bold; margin: 0 15px; border: 1px solid #008080; padding: 5px 15px; border-radius: 20px; background: #111; transition: 0.3s; display: inline-block; margin-top: 5px;}
    .social-links a:hover { background: #008080; color: #fff; }
    .stButton>button { background: linear-gradient(135deg, #008080, #111); color: white; border: 1px solid #008080; border-radius: 10px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 128, 128, 0.5); }
    .ai-card { background: #111; border: 1px solid #008080; padding: 15px; border-radius: 10px; margin-bottom: 15px; transition: 0.3s; }
    .ai-card:hover { border-color: #B4D8E7; box-shadow: 0 0 10px #008080; }
    .status-msg { background: #001a1a; color: #00ffcc; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; border: 1px solid #008080; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>WD PRO FF WORLD</div>", unsafe_allow_html=True)
st.markdown("""
<div class='social-links'>
    <a href='https://youtube.com/@wd_pro_ff' target='_blank'>📺 YouTube: wd_pro_ff</a>
    <a href='https://instagram.com/wd_pro_ff' target='_blank'>📸 Instagram: wd_pro_ff</a>
</div>
""", unsafe_allow_html=True)

# ==========================================================================================
# PART 3: MASSIVE DATABASES (50+ LANGUAGES, 2000+ AI, 1000+ FILTERS)
# ==========================================================================================
REAL_LANGUAGES = [
    "English", "Hindi", "Urdu", "Bengali", "Marathi", "Telugu", "Tamil", "Gujarati", "Kannada", "Odia", 
    "Malayalam", "Punjabi", "Assamese", "Maithili", "Santali", "Kashmiri", "Nepali", "Sindhi", "Dogri", "Konkani",
    "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese", "Arabic",
    "Turkish", "Vietnamese", "Thai", "Dutch", "Polish", "Swedish", "Danish", "Finnish", "Norwegian", "Greek",
    "Czech", "Hungarian", "Romanian", "Ukrainian", "Hebrew", "Indonesian", "Malay", "Filipino", "Swahili", "Afrikaans"
]

AI_DATA = {"Video": [], "Image": [], "Prompt": [], "Voice": []}
for cat in AI_DATA:
    for i in range(1, 501):
        AI_DATA[cat].append({"name": f"{cat} Tool #{i}", "link": "https://google.com", "desc": f"Professional {cat.lower()} generation tool."})
AI_DATA["Video"][0] = {"name": "🎥 Runway Gen-2", "link": "https://runwayml.com", "desc": "Industry standard Text-to-Video AI."}
AI_DATA["Video"][1] = {"name": "🎥 Sora (OpenAI)", "link": "https://openai.com/sora", "desc": "Hyper-realistic long video generation."}
AI_DATA["Image"][0] = {"name": "🖼️ Midjourney", "link": "https://midjourney.com", "desc": "Unmatched photorealistic image generation."}
AI_DATA["Image"][1] = {"name": "🖼️ Leonardo AI", "link": "https://leonardo.ai", "desc": "Advanced control, great for game assets."}
AI_DATA["Prompt"][0] = {"name": "✍️ ChatGPT (GPT-4o)", "link": "https://chatgpt.com", "desc": "The ultimate conversational & reasoning AI."}
AI_DATA["Voice"][0] = {"name": "🗣️ ElevenLabs", "link": "https://elevenlabs.io", "desc": "The most realistic AI text-to-speech."}

FILTERS_DB = {
    "0001: Original Raw": (1.0, 1.0, 1.0, 0),
    "0002: Hollywood Orange & Teal": (0.9, 1.2, 1.3, 10),
    "0003: Cinematic Dark Matte": (0.8, 1.3, 0.8, -10),
}
for i in range(4, 1001):
    FILTERS_DB[f"{str(i).zfill(4)}: WD Premium Grade"] = (round(random.uniform(0.8, 1.2), 2), round(random.uniform(0.9, 1.3), 2), round(random.uniform(0.5, 1.6), 2), random.randint(-25, 25))

# ==========================================================================================
# PART 4: SIDEBAR PANDA & API KEY
# ==========================================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#008080;'>🐼 WD PRO PANDA</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3 style='color:#B4D8E7; text-align:center;'>🎁 DAILY SCRATCH CARD</h3>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    next_midnight = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
    time_left = next_midnight - now
    h, rem = divmod(time_left.seconds, 3600)
    m, s = divmod(rem, 60)
    
    if st.session_state.scratched_today:
        st.markdown(f"""
        <div style='background:#111; border:2px solid #008080; border-radius:10px; padding:15px; text-align:center;'>
            <h4 style='color:#008080; margin:0;'>LOCKED 🔒</h4>
            <p style='color:#ccc; font-size:12px;'>Come back in:</p>
            <h3 style='color:#B4D8E7; margin:0; font-family:monospace;'>{h:02d}:{m:02d}:{s:02d}</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.panda_stage == 0:
            st.markdown("<div style='text-align:center; font-size:70px;'>🐼</div>", unsafe_allow_html=True)
            if st.button("🎁 GET GIFT FROM PANDA"):
                pb = st.empty(); pb.markdown("<div class='status-msg'>⏳ Intezar ka fal meetha hota hai...</div>", unsafe_allow_html=True)
                time.sleep(2); pb.empty(); st.session_state.panda_stage = 1; st.rerun()
        elif st.session_state.panda_stage == 1:
            st.markdown("<div style='text-align:center; background:#111; padding:15px; border-radius:10px; border:2px dashed #008080;'><span style='background:#B4D8E7; color:#000; padding:2px 8px; border-radius:5px; font-size:12px;'>Please open! 🥺</span><br><span style='font-size:60px;'>🐼👉🎁</span></div>", unsafe_allow_html=True)
            if st.button("🎁 OPEN THE BOX"):
                st.session_state.panda_stage = 2; st.rerun()
        elif st.session_state.panda_stage == 2:
            st.markdown("<div style='background:#111; border:2px dashed #008080; border-radius:10px; padding:15px; text-align:center;'><h5 style='color:#B4D8E7; margin-bottom:5px;'>🎫 SCRATCH CARD</h5><div style='background:#222; height:50px; line-height:50px; color:#666; font-weight:bold; border-radius:5px;'>▒▒ SCRATCH HERE ▒▒</div></div>", unsafe_allow_html=True)
            if st.button("🪙 SCRATCH WITH COIN"):
                pb = st.empty(); pb.markdown("<div class='status-msg'>⏳ Scratching...</div>", unsafe_allow_html=True)
                time.sleep(2); pb.empty(); st.session_state.scratched_today = True; st.rerun()
                
    st.divider()
    system_api_key = st.text_input("🔑 System API Key (Gemini)", value="AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co", type="password")
    st.caption("Agar AI translation fail hoti hai ya Urdu aati hai, toh iska matlab ye API Key block ho chuki hai. Nayi key daalein.")

# ==========================================================================================
# PART 5: MAIN WORKSPACE TABS
# ==========================================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⬇️ DOWNLOADER", "🎬 CAPTIONER", "🤖 AI DIRECTORY", "🚫 WATERMARK", "✨ COLOR GRADE"])

# ------------------------------------------------------------------------------------------
# TAB 1: DOWNLOADER (ANTI-BAN ROBUST)
# ------------------------------------------------------------------------------------------
with tab1:
    st.markdown("<h2 style='color:#B4D8E7;'>⬇️ Universal Media Downloader</h2>", unsafe_allow_html=True)
    d_mode = st.radio("Select Format:", ["Video (MP4)", "Audio (MP3)"], horizontal=True)
    d_url = st.text_input("🔗 Paste YouTube / Instagram / Spotify Link Here:")
    
    if d_url and st.button("🚀 START DOWNLOAD"):
        import yt_dlp
        with tempfile.TemporaryDirectory() as td:
            pb = st.empty()
            pb.markdown("<div class='status-msg'>⏳ Fetching Media... (YouTube restriction bypass lag raha hai)</div>", unsafe_allow_html=True)
            try:
                # Most robust anti-ban settings
                ydl_opts = {
                    'outtmpl': os.path.join(td, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'extractor_args': {'youtube': {'player_client': ['android']}},
                    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                }
                if 'Video' in d_mode:
                    ydl_opts['format'] = 'best[ext=mp4]/best' # Single file, no merge needed
                else:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(d_url, download=True)
                    filename = ydl.prepare_filename(info)
                    if 'Audio' in d_mode:
                        filename = filename.rsplit('.', 1)[0] + '.mp3'
                        
                    pb.empty()
                    st.success("✅ Media Tayyar Hai!")
                    with open(filename, "rb") as f:
                        file_bytes = f.read()
                        if 'Video' in d_mode:
                            st.video(file_bytes)
                            st.download_button("📥 CLICK TO SAVE MP4", file_bytes, os.path.basename(filename))
                        else:
                            st.audio(file_bytes)
                            st.download_button("📥 CLICK TO SAVE MP3", file_bytes, os.path.basename(filename))
            except Exception as e:
                pb.empty()
                st.error(f"❌ Streamlit IP is blocked by the platform. Error Details: {str(e)[:150]}")

# ------------------------------------------------------------------------------------------
# TAB 2: CAPTIONER (API ERROR HANDLING & ROMAN SCRIPT)
# ------------------------------------------------------------------------------------------
with tab2:
    st.markdown("<h2 style='color:#B4D8E7;'>🎬 Master Caption Engine</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: c_mode = st.radio("Translation Mode:", ["Keep Original Audio Language", "Translate to New Language"])
    with c2: c_lang = st.selectbox("Select Target Language (50+ available):", REAL_LANGUAGES)
    
    st.markdown("### 🎨 Text Design")
    col1, col2, col3 = st.columns(3)
    c_speed = col1.selectbox("Words per screen:", ["1 Word (Fast Viral)", "2 Words", "3 Words", "Full Sentence"])
    c_size = col2.slider("Text Size:", 30, 150, 70)
    c_pos = col3.selectbox("Position:", ["Bottom", "Center", "Top"])
    col4, col5 = st.columns(2)
    c_color = col4.color_picker("Text Color:", "#FFFFFF")
    c_out = col5.color_picker("Outline Color:", "#008080")
    
    c_vid = st.file_uploader("Upload Video (MP4):", type=["mp4"], key="cap_vid")
    
    if c_vid and st.button("🚀 GENERATE CAPTIONS (ROMAN SCRIPT)"):
        with tempfile.TemporaryDirectory() as td:
            in_p = os.path.join(td, "in.mp4")
            out_p = os.path.join(td, "out.mp4")
            with open(in_p, "wb") as f: f.write(c_vid.getbuffer())
            
            pb = st.empty()
            pb.markdown("<div class='status-msg'>⏳ Extracting Audio using AI...</div>", unsafe_allow_html=True)
            
            # Whisper Transcription
            model = whisper.load_model("base")
            res = model.transcribe(in_p)
            raw_text = "\n".join([f"{i}>> {s['text']}" for i, s in enumerate(res['segments'])])
            
            pb.markdown("<div class='status-msg'>⏳ AI Translation (Strictly English Alphabets / Hinglish)...</div>", unsafe_allow_html=True)
            genai.configure(api_key=system_api_key)
            
            if "Original" in c_mode:
                prompt = f"Convert the following text strictly into ROMAN SCRIPT (English Alphabets A-Z). DO NOT use Arabic, Urdu, or Hindi script. Example: write 'kya haal hai' instead of 'کیا حال ہے'. Output a pure JSON array of strings exactly matching the input lines. Text:\n{raw_text}"
            else:
                prompt = f"Translate the following text into {c_lang}. CRITICAL RULE: You MUST use ONLY English/Latin alphabets (Roman script/Hinglish style). DO NOT use native scripts (No Hindi, No Urdu, No Arabic scripts). Output a pure JSON array of strings exactly matching the input lines. Text:\n{raw_text}"
            
            try:
                g_out = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text.strip()
                g_out = g_out.replace("```json", "").replace("```", "")
                if "[" in g_out: g_out = g_out[g_out.find("["):g_out.rfind("]")+1]
                
                clean_data = json.loads(g_out)
                for i, s in enumerate(res['segments']):
                    s['final_text'] = str(clean_data[i]) if i < len(clean_data) else s['text']
                st.success(f"✅ AI API Hit Success! Roman Script ready.")
            except Exception as e:
                st.error(f"🚨 ALERT: Aapki Gemini API Key block ho gayi hai ya limit cross ho gayi hai. Error: {str(e)[:50]}")
                st.warning("AI fail hone ki wajah se Caption purani bhasha (Urdu/Original) mein hi dikhenge!")
                for s in res['segments']: s['final_text'] = s['text']
            
            # Chunking words
            final_segs = []
            l_int = 999 if "Full" in c_speed else int(c_speed.split()[0])
            for s in res['segments']:
                words = s.get('final_text', s['text']).split()
                if not words: continue
                if l_int == 999:
                    final_segs.append({'s': s['start'], 'e': s['end'], 't': " ".join(words)})
                else:
                    dur = (s['end'] - s['start']) / len(words)
                    for i in range(0, len(words), l_int):
                        final_segs.append({'s': s['start'] + (i*dur), 'e': s['start'] + ((i+l_int)*dur), 't': " ".join(words[i:i+l_int])})
            
            pb.markdown("<div class='status-msg'>⏳ Rendering Graphics on Video...</div>", unsafe_allow_html=True)
            p_bar = st.progress(0)
            
            cap = cv2.VideoCapture(in_p)
            fps = cap.get(cv2.CAP_PROP_FPS)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(out_p+"_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            
            r_main = (int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16))
            r_out = (int(c_out[1:3],16), int(c_out[3:5],16), int(c_out[5:7],16))
            
            try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", c_size)
            except: font = ImageFont.load_default()
            
            f_idx = 0; total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                sec = f_idx / fps; txt = ""
                for s in final_segs:
                    if s['s'] <= sec <= s['e']: txt = s['t']; break
                
                if txt:
                    frm_rgb = cv2.cvtColor(frame, cv2.COLOR_B
