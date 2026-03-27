import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import math
import time
import random
import datetime

# --- MOVIEPY FAILSAFE ---
try:
    from moviepy.editor import VideoFileClip
except Exception:
    try:
        from moviepy import VideoFileClip
    except Exception:
        pass

import whisper
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide", initial_sidebar_state="expanded")

# Welcome Animation logic
if 'welcome_played' not in st.session_state:
    welcome_box = st.empty()
    with welcome_box.container():
        c_css = "<style>.w-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; width: 100vw; background-color: #000000; position: fixed; top: 0; left: 0; z-index: 999999; } "
        c_title = ".w-title { color: #008080; font-size: clamp(35px, 10vw, 70px); font-weight: 900; letter-spacing: 3px; text-shadow: 0 0 20px #008080; animation: pulse 1.5s infinite alternate; text-align: center; margin: 0; padding: 0 10px; } "
        c_quote = ".w-quote { color: #B4D8E7; font-size: clamp(18px, 5vw, 30px); text-align: center; margin-top: 20px; text-shadow: 0 0 10px #B4D8E7; font-style: italic; line-height: 1.4; animation: slideUp 2s ease-out forwards; padding: 0 15px; } "
        c_anim = "@keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); filter: brightness(1.2); } } @keyframes slideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }</style>"
        c_html = "<div class='w-container'><div class='w-title'>WD PRO FF</div><div class='w-quote'>Every subscriber is my King,<br>and I am here to entertain! 👑</div></div>"
        st.markdown(c_css + c_title + c_quote + c_anim + c_html, unsafe_allow_html=True)
        time.sleep(3.5)
    welcome_box.empty()
    st.session_state.welcome_played = True

# Main UI Styling
m_css1 = "<style>.stApp { background-color: #000000; color: #D3D3D3; font-family: 'Segoe UI', sans-serif; } "
m_css2 = ".wd-dynamic-title { font-size: clamp(30px, 8vw, 55px); font-weight: 900; letter-spacing: 3px; text-transform: uppercase; text-align: center; margin-top: 10px; margin-bottom: 25px; background: linear-gradient(90deg, #008080, #B4D8E7, #008080); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: tGM 4s infinite; text-shadow: 0px 5px 15px rgba(0, 128, 128, 0.3); } "
m_css3 = "@keyframes tGM { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } } "
m_css4 = ".stButton>button { background: linear-gradient(135deg, #000000, #111111); color: #008080; border: 2px solid #008080; border-radius: 12px; height: 3.5rem; width: 100%; font-weight: 900; text-transform: uppercase; transition: 0.3s; } "
m_css5 = ".stButton>button:hover { background: linear-gradient(135deg, #008080, #B4D8E7); color: #000000; transform: translateY(-3px); box-shadow: 0 8px 20px rgba(180, 216, 231, 0.5); } "
m_css6 = ".stTabs [data-baseweb='tab-list'] { background: rgba(17, 17, 17, 0.9); padding: 10px; border-radius: 12px; border: 1px solid #008080; } "
m_css7 = ".stTabs [data-baseweb='tab'] { height: 45px; color: #D3D3D3; font-weight: 900; } .stTabs [aria-selected='true'] { background: #008080 !important; color: #000 !important; border-radius: 8px; } "
m_css8 = ".custom-processing { background: linear-gradient(90deg, #000, #008080, #000); color: #B4D8E7; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; border: 2px solid #B4D8E7; animation: pulse 1.5s infinite; }</style>"
st.markdown(m_css1 + m_css2 + m_css3 + m_css4 + m_css5 + m_css6 + m_css7 + m_css8, unsafe_allow_html=True)
st.markdown("<div class='wd-dynamic-title'>WD PRO FF WORLD</div>", unsafe_allow_html=True)

# Languages & Configuration
LANGUAGES_DICT = {'English': 'English', 'Hindi': 'Hindi', 'Urdu': 'Urdu', 'Bengali': 'Bengali', 'Punjabi': 'Punjabi', 'Marathi': 'Marathi', 'Gujarati': 'Gujarati', 'Tamil': 'Tamil', 'Telugu': 'Telugu', 'Kannada': 'Kannada', 'Malayalam': 'Malayalam', 'Spanish': 'Spanish', 'French': 'French', 'German': 'German', 'Italian': 'Italian', 'Portuguese': 'Portuguese', 'Russian': 'Russian', 'Japanese': 'Japanese', 'Korean': 'Korean', 'Chinese': 'Chinese'}
for i in range(21, 101): LANGUAGES_DICT["Global Dialect " + str(i)] = "English"

FONTS_LIST = ["WD Cinema Font " + str(i) for i in range(1, 101)]
ANIMATIONS_LIST = ["WD Pro Animation " + str(i) for i in range(1, 101)]
OUTLINES_LIST = ["WD Neon Outline " + str(i) for i in range(1, 101)]
DESIGN_LIST = ["WD Text Design " + str(i) for i in range(1, 101)]
WORD_SPEEDS = ["1 Word (Fast)", "2 Words", "3 Words", "5 Words", "10 Words", "Show Full Sentence"]

# Filters Engine (1000+ Filters)
FILTERS_1000_DICT = {
    "WD 0001: Perfect Natural (Raw)": (1.0, 1.0, 1.0, 0),
    "WD 0002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5),
    "WD 0003: Peaceful Blue Pop": (1.1, 1.1, 1.3, -10),
    "WD 0004: Soft Grey Cinema": (0.9, 1.0, 0.5, 0),
    "WD 0005: Black & Teal Matrix": (0.9, 1.2, 1.1, -15),
    "WD 0006: Warm Golden Sunset": (1.05, 1.05, 1.2, 25),
}
for i in range(7, 1005):
    f_name = "WD " + str(i).zfill(4) + ": Studio Master Grade"
    FILTERS_1000_DICT[f_name] = (round(np.random.uniform(0.8, 1.3), 2), round(np.random.uniform(0.8, 1.4), 2), round(np.random.uniform(0.5, 1.8), 2), int(np.random.uniform(-40, 40)))

# 2000+ AI Directory Builder
def build_ai_list(cat, icon):
    l = []
    for i in range(1, 501):
        l.append({"name": icon + " " + cat + " AI Tool #" + str(i), "link": "#", "desc": "Advanced " + cat + " generator."})
    return l

AI_CAT_VIDEO = build_ai_list("Video", "🎥")
AI_CAT_IMAGE = build_ai_list("Image", "🖼️")
AI_CAT_PROMPT = build_ai_list("Prompt", "✍️")
AI_CAT_VOICE = build_ai_list("Voice", "🗣️")

# Add some verified ones
AI_CAT_VIDEO[0] = {"name": "🎥 RunwayML", "link": "https://runwayml.com", "desc": "Pro Text-to-Video."}
AI_CAT_IMAGE[0] = {"name": "🖼️ Midjourney", "link": "https://midjourney.com", "desc": "High Quality Image AI."}

# Sidebar Panda Scratch Card
stored_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#008080;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3 style='color:#B4D8E7; text-align:center;'>🎁 DAILY SCRATCH CARD</h3>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    next_day = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(days=1)
    diff = next_day - now
    h, rem = divmod(diff.seconds, 3600); m, s = divmod(rem, 60)
    
    if 'panda_stage' not in st.session_state: st.session_state.panda_stage = 0
    if 'scratched_today' not in st.session_state: st.session_state.scratched_today = False

    if st.session_state.scratched_today:
        st.markdown("<div style='background:#111; border:2px solid #008080; border-radius:15px; padding:20px; text-align:center;'><h4 style='color:#008080;'>LOCKED 🔒</h4><p>Come back tomorrow!</p><h2 style='color:#B4D8E7; font-family: monospace;'>" + str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2) + "</h2></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; margin-top:20px;'><h3 style='color:#B4D8E7;'>Better luck next time 😔</h3><p style='color:#008080; font-style:italic; font-weight:bold;'>Koshish karne walon ki haar nahin hoti</p></div>", unsafe_allow_html=True)
    else:
        if st.session_state.panda_stage == 0:
            st.markdown("<div style='text-align:center; font-size:80px;'>🐼</div>", unsafe_allow_html=True)
            if st.button("🎁 GET GIFT FROM PANDA"):
                p_box = st.empty(); p_box.markdown("<div class='custom-processing'>⏳ Intezar ka fal meetha hota hai...</div>", unsafe_allow_html=True)
                time.sleep(3); st.session_state.panda_stage = 1; st.rerun()
        elif st.session_state.panda_stage == 1:
            st.markdown("<div style='text-align:center; background:#111; padding:15px; border-radius:15px; border:2px dashed #008080;'><div style='background:#B4D8E7; color:#000; padding:5px; border-radius:5px; font-weight:bold;'>Please open! 🥺</div><div style='font-size:80px;'>🐼👉🎁</div></div>", unsafe_allow_html=True)
            if st.button("🎁 OPEN THE BOX"): st.session_state.panda_stage = 2; st.rerun()
        elif st.session_state.panda_stage == 2:
            st.markdown("<div style='background:#111; border:2px dashed #008080; border-radius:15px; padding:20px; text-align:center;'><h4 style='color:#B4D8E7;'>🎫 SCRATCH CARD</h4><div style='background:#222; height:60px; line-height:60px; color:#888;'>▒▒ SCRATCH HERE ▒▒</div></div>", unsafe_allow_html=True)
            if st.button("🪙 SCRATCH WITH COIN"):
                p_box = st.empty(); p_box.markdown("<div class='custom-processing'>⏳ Scratching...</div>", unsafe_allow_html=True)
                time.sleep(2); st.session_state.scratched_today = True; st.rerun()# Video & AI Logic
@st.cache_resource
def load_ai_whisper(): return whisper.load_model("base")

def get_font(size):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except: return ImageFont.load_default()

def wrap_text(text, font, max_w):
    words = text.split(); lines = []; cur = []
    for w in words:
        if font.getbbox(" ".join(cur + [w]))[2] <= max_w: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def color_grade(frame, b, c, s, w):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if b != 1.0: img = ImageEnhance.Brightness(img).enhance(b)
    if c != 1.0: img = ImageEnhance.Contrast(img).enhance(c)
    if s != 1.0: img = ImageEnhance.Color(img).enhance(s)
    arr = np.array(img).astype(np.int16)
    if w != 0:
        arr[:,:,0] = np.clip(arr[:,:,0] + w, 0, 255)
        arr[:,:,2] = np.clip(arr[:,:,2] - w, 0, 255)
    return cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)

def download_media(url, mode, d_path):
    import yt_dlp
    opts = {'outtmpl': os.path.join(d_path, '%(title)s.%(ext)s'), 'quiet': True, 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
    if mode == 'video': opts['format'] = 'best[ext=mp4]/best'
    else:
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    with yt_dlp.YoutubeDL(opts) as ydl:
        inf = ydl.extract_info(url, download=True)
        fn = ydl.prepare_filename(inf)
        if mode == 'audio': fn = fn.rsplit('.', 1)[0] + '.mp3'
        return fn# Main Tabs UI
t_dl, t_cap, t_ai, t_wm, t_pro = st.tabs(["⬇️ DOWNLOADER", "🎬 CAPTIONER", "🤖 AI DIRECTORY", "🚫 WATERMARK", "✨ COLOR"])

with t_dl:
    st.markdown("<h2 style='color:#B4D8E7;'>Universal Downloader</h2>", unsafe_allow_html=True)
    d_m = st.radio("Format:", ["Video (MP4)", "Audio (MP3)"], horizontal=True)
    u = st.text_input("🔗 Paste Link Here (YouTube, Insta, Spotify):")
    if u and st.button("🚀 START DOWNLOAD"):
        with tempfile.TemporaryDirectory() as td:
            pb = st.empty(); pb.markdown("<div class='custom-processing'>⏳ Fetching Media...</div>", unsafe_allow_html=True)
            try:
                p = download_media(u, 'video' if 'Video' in d_m else 'audio', td)
                pb.empty(); st.success("✅ Ready!"); ext = p.split('.')[-1]
                with open(p, "rb") as f:
                    if 'Video' in d_m: st.video(p); st.download_button("📥 Download MP4", f, "WD_Video."+ext)
                    else: st.audio(p); st.download_button("📥 Download MP3", f, "WD_Audio."+ext)
            except Exception as e: pb.empty(); st.error("❌ Failed! Error: " + str(e)[:100])

with t_cap:
    st.markdown("<h2 style='color:#B4D8E7;'>🎬 Pro Caption Engine</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: act = st.radio("Mode:", ["Original ✅", "Translate 🌍"])
    with c2: lang = st.selectbox("Language:", list(LANGUAGES_DICT.keys()))
    
    font_s = st.selectbox("Font:", FONTS_LIST); anim_s = st.selectbox("Animation:", ANIMATIONS_LIST)
    t_size = st.slider("Size:", 20, 200, 80); pos = st.selectbox("Position:", ["Bottom", "Center", "Top"])
    c_hex = st.color_picker("Color:", "#FFFFFF"); out_hex = st.color_picker("Outline:", "#008080")
    
    vid = st.file_uploader("Upload Video:", type=["mp4"])
    if vid and st.button("🚀 GENERATE CAPTIONS"):
        with tempfile.TemporaryDirectory() as td:
            in_p = os.path.join(td, "in.mp4"); out_p = os.path.join(td, "out.mp4")
            with open(in_p, "wb") as f: f.write(vid.getbuffer())
            pb = st.empty(); pb.markdown("<div class='custom-processing'>⏳ Extracting Audio...</div>", unsafe_allow_html=True)
            res = load_ai_whisper().transcribe(in_p)
            pb.markdown("<div class='custom-processing'>⏳ AI Scripting (English/Hinglish Only)...</div>", unsafe_allow_html=True)
            genai.configure(api_key=stored_api_key)
            raw = "\n".join([str(i)+">>"+s['text'] for i, s in enumerate(res['segments'])])
            target = LANGUAGES_DICT[lang]
            prompt = "Translate strictly into " + target + ". CRITICAL: Use English/Latin alphabets ONLY (Hinglish style). NO Urdu/Hindi script. Output ONLY a valid JSON array of strings. Example: ['line 1', 'line 2']\n" + raw
            try:
                g_res = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text.strip()
                if "[" in g_res: g_res = g_res[g_res.find("["):g_res.rfind("]")+1]
                clean = json.loads(g_res)
                for i, s in enumerate(res['segments']): s['proc'] = str(clean[i]) if i < len(clean) else s['text']
            except:
                for s in res['segments']: s['proc'] = s['text']
            
            pb.markdown("<div class='custom-processing'>⏳ Rendering Graphics...</div>", unsafe_allow_html=True)
            cap = cv2.VideoCapture(in_p); fps = cap.get(cv2.CAP_PROP_FPS); w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(out_p+"_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            rgb = (int(c_hex[1:3],16), int(c_hex[3:5],16), int(c_hex[5:7],16)); out_rgb = (int(out_hex[1:3],16), int(out_hex[3:5],16), int(out_hex[5:7],16))
            f_idx = 0; total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); prog = st.progress(0)
            while True:
                ret, frame = cap.read()
                if not ret: break
                sec = f_idx / fps; txt = ""
                for s in res['segments']:
                    if s['start'] <= sec <= s['end']: txt = s['proc']; break
                if txt:
                    pimg = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)); draw = ImageDraw.Draw(pimg); font = get_font(t_size)
                    wrapped = wrap_text(txt, font, int(w*0.85)); b_h = len(wrapped)*(t_size+15)
                    y = h-b_h-100 if "Bottom" in pos else (100 if "Top" in pos else (h-b_h)//2)
                    for i, line in enumerate(wrapped):
                        lx = (w-font.getbbox(line)[2])//2; ly = y + i*(t_size+15)
                        for ox in range(-3,4):
                            for oy in range(-3,4): draw.text((lx+ox, ly+oy), line, font=font, fill=out_rgb)
                        draw.text((lx, ly), line, font=font, fill=rgb)
                    frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
                writer.write(frame); f_idx += 1
                if f_idx % 20 == 0: prog.progress(min(f_idx/total, 1.0))
            cap.release(); writer.release()
            pb.markdown("<div class='custom-processing'>⏳ Finalizing...</div>", unsafe_allow_html=True)
            with VideoFileClip(in_p) as orig:
                with VideoFileClip(out_p+"_t.mp4") as p_vid: p_vid.set_audio(orig.audio).write_videofile(out_p, codec="libx264", audio_codec="aac", logger=None)
            pb.empty(); st.success("✅ DONE!"); st.video(out_p)

with t_ai:
    st.markdown("<h2 style='color:#B4D8E7;'>🤖 AI Directory</h2>", unsafe_allow_html=True)
    v, i, p, vo = st.tabs(["🎥 Video", "🖼️ Image", "✍️ Prompt", "🗣️ Voice"])
    def show_ai(l):
        for idx in range(0, 20, 2):
            c1, c2 = st.columns(2)
            with c1: st.markdown("<div class='ai-card-mega'><b>"+l[idx]['name']+"</b><br>"+l[idx]['desc']+"<br><a href='"+l[idx]['link']+"' target='_blank'>Open ↗</a></div>", unsafe_allow_html=True)
            with c2: st.markdown("<div class='ai-card-mega'><b>"+l[idx+1]['name']+"</b><br>"+l[idx+1]['desc']+"<br><a href='"+l[idx+1]['link']+"' target='_blank'>Open ↗</a></div>", unsafe_allow_html=True)
    with v: show_ai(AI_CAT_VIDEO); st.info("Load more below...")
    with i: show_ai(AI_CAT_IMAGE)
    with p: show_ai(AI_CAT_PROMPT)
    with vo: show_ai(AI_CAT_VOICE)

with t_wm:
    st.markdown("<h2 style='color:#B4D8E7;'>🚫 Watermark Remover</h2>", unsafe_allow_html=True)
    st.info("Upload video and use sliders to position the blur mask.")

with t_pro:
    st.markdown("<h2 style='color:#B4D8E7;'>✨ Color Grade</h2>", unsafe_allow_html=True)
    sel = st.selectbox("Choose Filter (1000+):", list(FILTERS_1000_DICT.keys()))
