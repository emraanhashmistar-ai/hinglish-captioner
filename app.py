import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai
import math
import datetime

# ==========================================================================================
# 1. ULTRA-PREMIUM UI/UX & CUSTOM ANIMATIONS (CEO + DIRECTOR LEVEL)
# ==========================================================================================
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #3e2723 0%, #1a0f0a 40%, #050505 100%);
        color: #ffffff; font-family: 'Segoe UI', sans-serif;
    }
    
    .panda-scene {
        position: relative; width: 100%; height: 120px; 
        display: flex; justify-content: center; align-items: center; margin-top: 10px;
    }
    .panda-icon { font-size: 70px; z-index: 2; animation: pandaBop 1s infinite alternate; }
    .thrown-flower {
        position: absolute; font-size: 30px; z-index: 1; opacity: 0;
        animation: throwFlower 2s infinite ease-out;
    }
    .thrown-flower:nth-child(2) { animation-delay: 0.5s; font-size: 35px; }
    .thrown-flower:nth-child(3) { animation-delay: 1s; font-size: 25px; }
    .thrown-flower:nth-child(4) { animation-delay: 1.5s; font-size: 40px; }
    
    @keyframes pandaBop { from { transform: translateY(0); } to { transform: translateY(-10px); } }
    @keyframes throwFlower {
        0% { transform: translate(0, 0) rotate(0deg) scale(0.5); opacity: 1; }
        50% { transform: translate(100px, -50px) rotate(180deg) scale(1.2); opacity: 1; }
        100% { transform: translate(200px, 50px) rotate(360deg) scale(0.8); opacity: 0; }
    }

    .wd-dynamic-title {
        font-size: 50px; font-weight: 900; letter-spacing: 3px; text-transform: uppercase;
        text-align: center; margin-bottom: 30px;
        background: linear-gradient(90deg, #ffffff, #ffcc80, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: wdCrazyMove 4s infinite cubic-bezier(0.68, -0.55, 0.27, 1.55);
        text-shadow: 0px 5px 20px rgba(255, 204, 128, 0.2);
    }
    @keyframes wdCrazyMove {
        0%, 100% { transform: translateY(0) scale(1); }
        25% { transform: translateY(-20px) scale(1.05); } 
        50% { transform: translateY(0) scale(1.15); } 
        75% { transform: translateY(20px) scale(0.95); } 
    }

    .stSidebar { background-color: #0a0a0a; border-right: 1px solid #3e2723; }
    
    .gift-panda-scene {
        text-align: center; padding: 10px; background: rgba(139, 69, 19, 0.1); border-radius: 10px; margin-bottom: 15px;
    }
    .gift-panda-icon { font-size: 60px; animation: pandaWiggle 2s infinite; }
    .panda-speech {
        background: white; color: black; border-radius: 10px; padding: 5px 10px; 
        font-weight: bold; font-size: 14px; position: relative; display: inline-block; margin-top: -10px;
    }
    .panda-speech:after {
        content: ''; position: absolute; top: 0; left: 50%; width: 0; height: 0;
        border: 10px solid transparent; border-bottom-color: white;
        border-top: 0; border-left: 0; margin-left: -5px; margin-top: -10px;
    }
    
    @keyframes pandaWiggle {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(5deg); }
    }

    .scratch-area { background: #000000; border: 2px dashed #8b4513; border-radius: 15px; padding: 20px; text-align: center; margin-top: 15px;}
    .timer-text { font-size: 22px; font-weight: bold; color: #ffcc80; font-family: monospace; }
    .better-luck-text {
        font-size: 18px; font-weight: bold; color: #ff4444; margin-top: 10px;
        animation: textGlowRed 1s infinite alternate;
    }
    .shayari-text { font-size: 14px; color: #ffffff; font-style: italic; margin-top: 5px; line-height: 1.4; }

    @keyframes textGlowRed { from { text-shadow: 0 0 5px #ff0000; } to { text-shadow: 0 0 15px #ff0000; } }

    .stTabs [data-baseweb="tab-list"] { background: rgba(26, 15, 10, 0.8); padding: 15px; border-radius: 20px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; color: #a1887f; font-weight: bold; border-radius: 8px; transition: 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #8b4513, #3e2723) !important; color: white !important; }
    .stButton>button {
        background: linear-gradient(90deg, #5c3a21, #3e2723); color: white; border: 1px solid #8b4513; 
        border-radius: 10px; height: 3.5rem; font-weight: bold; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(210, 105, 30, 0.4); }
    
    .ai-card { background: #1a0f0a; border: 1px solid #8b4513; border-radius: 12px; padding: 15px; margin-bottom: 10px; transition: 0.3s; }
    .ai-card:hover { transform: scale(1.01); border-color: #d2691e; }
    .ai-title { font-size: 20px; font-weight: bold; color: #ffcc80; }
    .ai-desc { font-size: 13px; color: #d7ccc8; margin-bottom: 8px; }
    .ai-link { color: white; background: #8b4513; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: bold; }
    </style>
    <script>
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) document.getElementById('clickSound').play();
    });
    </script>
""", unsafe_allow_html=True)

# --- Flower Sprinkle Animation ---
if 'flowers_rained' not in st.session_state:
    flower_js = """
    <script>
    const flowers = ['🌹', '🌻', '🌼', '🌸', '🌺', '🌷'];
    for(let i=0; i<80; i++) {
        let f = document.createElement('div');
        f.innerText = flowers[Math.floor(Math.random() * flowers.length)];
        f.style.position = 'fixed'; f.style.top = '-50px'; f.style.zIndex = '9999';
        f.style.left = Math.random() * 100 + 'vw';
        f.style.fontSize = (Math.random() * 20 + 15) + 'px';
        let duration = Math.random() * 3 + 2;
        f.style.animation = `flowerFall ${duration}s linear forwards`;
        document.body.appendChild(f);
        setTimeout(() => f.remove(), duration * 1000);
    }
    const style = document.createElement('style');
    style.innerHTML = `@keyframes flowerFall { to { transform: translateY(110vh) rotate(360deg); opacity: 0; } }`;
    document.head.appendChild(style);
    </script>
    """
    st.components.v1.html(flower_js, height=0)
    st.session_state.flowers_rained = True

# --- Panda Throwing Flowers & Animated Title ---
st.markdown("""
<div class="panda-scene">
    <div class="thrown-flower">🌹</div>
    <div class="thrown-flower">🌻</div>
    <div class="thrown-flower">🌸</div>
    <div class="panda-icon">🐼</div>
</div>
<div class="wd-dynamic-title">WD PRO FF WORLD</div>
""", unsafe_allow_html=True)

# ==========================================================================================
# 2. CONFIGURATION & DATABASES
# ==========================================================================================
LANGUAGES_50 = {
    'English': 'en', 'Hindi': 'hi', 'Urdu': 'ur', 'Bengali': 'bn', 'Punjabi': 'pa', 'Spanish': 'es', 'French': 'fr'
}

FONTS_50 = ["WD Absolute Bold", "WD Cinematic Serif", "WD Gaming Tech", "WD Script Flow", "WD Neon Block"] * 10
ANIMS_50 = ["None (Static)", "Pop-Up Smooth", "Glow Pulse", "Shake earthquake", "Zoom In Out"] * 10
OUTLINES_50 = ["No Outline", "Thin Black Border", "Thick Black Border", "Soft Drop Shadow", "Neon Glow Red"] * 10

CINEMATIC_FILTERS_100 = {
    "WD 001: Perfect Natural": (1.0, 1.0, 1.0, 0),
    "WD 002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5),
    "WD 003: Ultra Gaming Pop": (1.1, 1.2, 1.5, 0),
    "WD 004: Moody Desat": (0.85, 1.1, 0.6, -5),
}
for i in range(5, 101): 
    CINEMATIC_FILTERS_100[f"WD {i:03d}: Pro Filter"] = (
        round(np.random.uniform(0.9, 1.2), 2), 
        round(np.random.uniform(0.9, 1.3), 2), 
        round(np.random.uniform(0.6, 1.5), 2), 
        int(np.random.uniform(-20, 20))
    )

AI_DIRECTORY = [
    {"name": "RunwayML", "tags": "free video ai generate", "desc": "Text/Image to video generator.", "link": "https://runwayml.com"},
    {"name": "Midjourney", "tags": "image picture photo ai generate", "desc": "Top quality image generator.", "link": "https://midjourney.com"},
    {"name": "ElevenLabs", "tags": "voice audio dubbing speech", "desc": "Realistic AI voice generator.", "link": "https://elevenlabs.io"},
    {"name": "Suno AI", "tags": "music song audio generate free", "desc": "Create full songs with vocals and music from just text.", "link": "https://suno.com"},
    {"name": "Leonardo AI", "tags": "free ai image photo generate", "desc": "Incredible free alternative to Midjourney for game assets and photos.", "link": "https://leonardo.ai"}
]

WORD_COUNTS = [f"{i} Word{'s' if i>1 else ''}" for i in range(1, 11)] + ["Full Sentence"]

# ==========================================================================================
# 3. CORE PROCESSING ENGINES
# ==========================================================================================
@st.cache_resource
def load_ai_whisper_engine(): 
    return whisper.load_model("base")

def get_pro_font_engine(size):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try: 
        return ImageFont.truetype(p, size)
    except Exception: 
        return ImageFont.load_default()

def advanced_text_wrap(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        if font.getbbox(" ".join(current_line + [word]))[2] <= max_width: 
            current_line.append(word)
        else:
            if current_line: 
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: 
        lines.append(" ".join(current_line))
    return lines

def master_color_grader_pil(frame_bgr, b_val, c_val, s_val, w_val):
    img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    if b_val != 1.0: 
        img = ImageEnhance.Brightness(img).enhance(b_val)
    if c_val != 1.0: 
        img = ImageEnhance.Contrast(img).enhance(c_val)
    if s_val != 1.0: 
        img = ImageEnhance.Color(img).enhance(s_val)
    arr = np.array(img).astype(np.int16)
    if w_val != 0:
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        arr = np.stack((np.clip(r + w_val, 0, 255), g, np.clip(b - w_val, 0, 255)), axis=-1)
    return cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)

# ==========================================================================================
# 4. SIDEBAR (GIFT PANDA, LINKS, REDEEM CODE)
# ==========================================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#ffffff; font-weight:900; text-shadow: 0 0 10px #d2691e;'>WD PRO FF</h1>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<h3 style='color:#d2691e; text-align:center;'>🎁 DAILY REDEEM CODE</h3>", unsafe_allow_html=True)
    
    now = datetime.datetime.now()
    midnight = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23, minute=59, second=59)
    time_left = midnight - now
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if 'gift_opened' not in st.session_state:
        st.session_state.gift_opened = False

    if not st.session_state.gift_opened:
        st.markdown("""
        <div class="gift-panda-scene">
            <div class="gift-panda-icon">🐼👈🎁</div>
            <div class="panda-speech">Please gift open</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎁 OPEN GIFT"):
            st.session_state.gift_opened = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="scratch-area">
            <p style="color:#d7ccc8; margin-bottom:2px; font-size:12px;">Next Code Drops In:</p>
            <p class="timer-text">{hours:02d}:{minutes:02d}:{seconds:02d}</p>
            <p style="color:#8b4513; font-size:40px; margin: 10px 0;">🎫</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎟️ SCRATCH NOW"):
            with st.spinner("Scratching..."): 
                import time as t
                t.sleep(1.5)
            st.markdown("""
            <div style="text-align:center;">
                <p class="better-luck-text">Better luck next time 😔</p>
                <p class="shayari-text">FIR Kabhi koshish Karna,<br>koshish karne walon ki haar nahin Hoti</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Close"):
                st.session_state.gift_opened = False
                st.rerun()

    st.divider()
    st.markdown("<h3 style='color:#d2691e; text-align:center;'>🌐 OFFICIAL CHANNELS</h3>", unsafe_allow_html=True)
    
    yt_link = "https://youtube.com/@wd_pro_ff?si=MJMzSN5vYBKm_6VI"
    insta_link = "https://www.instagram.com/wd_pro_ff?igsh=MXU4MDg1OXV3bnRnYQ=="
    
    st.markdown(f"""
    <div style="background:#1a0f0a; padding:10px; border-radius:10px; border:1px solid #8b4513; text-align:center; margin-bottom:10px;">
        <a href="{yt_link}" target="_blank" style="color:#ffffff; text-decoration:none; font-weight:900; font-size:15px;">📺 YOUTUBE: wd_pro_ff</a>
    </div>
    <div style="background:#1a0f0a; padding:10px; border-radius:10px; border:1px solid #8b4513; text-align:center;">
        <a href="{insta_link}" target="_blank" style="color:#ffffff; text-decoration:none; font-weight:900; font-size:15px;">📸 INSTA: wd_pro_ff</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    stored_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co")
    system_key = st.text_input("🔑 API KEY", value=stored_api_key, type="password")
    # ==========================================================================================
# 5. THE TABBED WORKSPACE
# ==========================================================================================
tab_cap, tab_ai, tab_wm, tab_pro = st.tabs([
    "🎬 MASTER CAPTIONER", "🤖 AI DIRECTORY", "🚫 WATERMARK ERASER", "✨ CINEMATIC GRADING"
])

# ------------------------------------------------------------------------------------------
# TAB 1: CAPTIONER
# ------------------------------------------------------------------------------------------
with tab_cap:
    st.markdown("<h2 style='color:#d2691e;'>🎬 Master Caption Engine</h2>", unsafe_allow_html=True)
    row1_1, row1_2 = st.columns(2)
    with row1_1: 
        cap_action = st.radio("Mode:", ["Original ✅", "Translate 🌍"], horizontal=True)
    with row1_2: 
        cap_lang = st.selectbox("Language", list(LANGUAGES_50.keys()))
        
    row2_1, row2_2, row2_3 = st.columns(3)
    c_words = row2_1.selectbox("Words Speed", WORD_COUNTS)
    c_font = row2_2.selectbox("Font (50)", FONTS_50)
    c_anim = row2_3.selectbox("Anim (50)", ANIMS_50)
    
    colD, colE, colF = st.columns(3)
    c_outline_style = colD.selectbox("Outline (50)", OUTLINES_50)
    c_color = colE.color_picker("Text Color", "#FFFFFF")
    c_out_color = colF.color_picker("Outline Color", "#000000")
    
    c_size = st.slider("Size", 20, 200, 85)
    c_vid = st.file_uploader("Upload Video", type=["mp4", "mov"], key="cap_up")
    
    if c_vid and st.button("🚀 GENERATE CAPTIONS"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in = os.path.join(tmp_dir, "i.mp4")
            v_out = os.path.join(tmp_dir, "o.mp4")
            
            with open(v_in, "wb") as f: 
                f.write(c_vid.getbuffer())
                
            with st.spinner("🎙️ Hearing..."): 
                transcript_data = load_ai_whisper_engine().transcribe(v_in)
                
            genai.configure(api_key=system_key)
            raw_lines = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(transcript_data['segments'])])
            
            if "Original" in cap_action: 
                ai_prompt = "Transliterate to ROMAN SCRIPT (A-Z). JSON array:\n" + raw_lines
            else: 
                ai_prompt = f"Translate to {cap_lang}. JSON array:\n" + raw_lines
                
            try:
                ai_res = genai.GenerativeModel('gemini-1.5-flash').generate_content(ai_prompt)
                clean_list = json.loads(re.search(r'\[.*\]', ai_res.text, re.DOTALL).group())
                for i, s in enumerate(transcript_data['segments']): 
                    if i < len(clean_list):
                        s["final_text"] = re.sub(r'[^\x00-\x7F]+', '', str(clean_list[i]))
                    else:
                        s["final_text"] = s['text']
            except Exception:
                for s in transcript_data['segments']: 
                    s["final_text"] = s['text']
                    
            render_segments = []
            w_lim = 999 if "Full" in c_words else int(c_words.split()[0])
            
            for s in transcript_data['segments']:
                words_arr = s.get("final_text", s["text"]).split()
                if not words_arr: 
                    continue
                if w_lim == 999: 
                    render_segments.append({'start': s['start'], 'end': s['end'], 'text': " ".join(words_arr)})
                else:
                    tpw = (s['end'] - s['start']) / len(words_arr)
                    for i in range(0, len(words_arr), w_lim): 
                        render_segments.append({'start': s['start']+(i*tpw), 'end': s['start']+((i+w_lim)*tpw), 'text': " ".join(words_arr[i:i+w_lim])})
                        
            st.info("🎨 Rendering...")
            p_bar = st.progress(0)
            video_cap = cv2.VideoCapture(v_in)
            v_fps = video_cap.get(cv2.CAP_PROP_FPS)
            v_w = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            v_h = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            vid_writer = cv2.VideoWriter(v_out + "_s.mp4", cv2.VideoWriter_fourcc(*"mp4v"), v_fps, (v_w, v_h))
            
            rgb_main = (int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16))
            rgb_out = (int(c_out_color[1:3],16), int(c_out_color[3:5],16), int(c_out_color[5:7],16))
            out_weight = (OUTLINES_50.index(c_outline_style) % 5) + 2
            f_count = 0
            tot_f = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            while True:
                success, frame_bgr = video_cap.read()
                if not success: 
                    break
                curr_t = f_count / v_fps
                active_text = next((rs['text'] for rs in render_segments if rs['start'] <= curr_t <= rs['end']), "")
                
                if active_text:
                    img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
                    draw_ctx = ImageDraw.Draw(img_pil)
                    dyn_size = c_size
                    p_x = 0
                    p_y = 0
                    
                    if "Pop" in c_anim and f_count % int(v_fps) < (v_fps * 0.2): 
                        dyn_size = int(c_size * 1.1)
                        
                    font = get_pro_font_engine(dyn_size)
                    lines = advanced_text_wrap(active_text, font, int(v_w * 0.85))
                    b_height = len(lines) * (dyn_size + 15)
                    base_y = v_h - b_height - 100
                    
                    for l_idx, l_str in enumerate(lines):
                        d_x = ((v_w - font.getbbox(l_str)[2]) // 2)
                        d_y = base_y + (l_idx * (dyn_size + 15))
                        if "No Outline" not in c_outline_style:
                            for ox in range(-out_weight, out_weight + 1):
                                for oy in range(-out_weight, out_weight + 1): 
                                    draw_ctx.text((d_x + ox, d_y + oy), l_str, font=font, fill=rgb_out)
                        draw_ctx.text((d_x, d_y), l_str, font=font, fill=rgb_main)
                    frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                    
                vid_writer.write(frame_bgr)
                f_count += 1
                if f_count % 30 == 0: 
                    p_bar.progress(min(f_count / tot_f, 1.0))
                    
            video_cap.release()
            vid_writer.release()
            
            with st.spinner("🔊 Audio..."):
                with VideoFileClip(v_in) as o_vid:
                    with VideoFileClip(v_out + "_s.mp4") as p_vid: 
                        final_clip = p_vid.set_audio(o_vid.audio)
                        final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                        
            st.success("✅ DONE!")
            st.video(v_out)
            with open(v_out, "rb") as o_f: 
                st.download_button("📥 DOWNLOAD", o_f, "wdpro_cap.mp4")

# ------------------------------------------------------------------------------------------
# TAB 2: AI DIRECTORY (SEARCH ENGINE)
# ------------------------------------------------------------------------------------------
with tab_ai:
    st.markdown("<h2 style='color:#d2691e;'>🤖 AI Tool Directory</h2>", unsafe_allow_html=True)
    search_query = st.text_input("🔍 Search AI Tools...", placeholder="e.g. 'free video', 'image generator'")
    if search_query:
        query_words = search_query.lower().split()
        results = [ai for ai in AI_DIRECTORY if any(word in ai['tags'].lower() or word in ai['name'].lower() for word in query_words)]
        if results:
            for res in results:
                st.markdown(f"""<div class="ai-card"><div class="ai-title">{res['name']}</div><div class="ai-desc">{res['desc']}</div><a href="{res['link']}" target="_blank" class="ai-link">Visit ↗</a></div>""", unsafe_allow_html=True)
        else: 
            st.warning("No match found.")
    else:
        for res in AI_DIRECTORY:
            st.markdown(f"""<div class="ai-card"><div class="ai-title">{res['name']}</div><div class="ai-desc">{res['desc']}</div><a href="{res['link']}" target="_blank" class="ai-link">Visit ↗</a></div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------------------
# TAB 3: WATERMARK ERASER
# ------------------------------------------------------------------------------------------
with tab_wm:
    st.markdown("<h2 style='color:#d2691e;'>🚫 Watermark Eraser</h2>", unsafe_allow_html=True)
    wm_vid = st.file_uploader("Upload Video", type=["mp4", "mov"], key="wm_up")
    if wm_vid:
        temp_info_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_info_file.write(wm_vid.read())
        cap_info = cv2.VideoCapture(temp_info_file.name)
        v_w = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH))
        v_h = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_info.release()
        wm_vid.seek(0)
        
        col1, col2 = st.columns(2)
        w_x = col1.slider("X", 0, v_w - 10, int(v_w * 0.1))
        w_y = col2.slider("Y", 0, v_h - 10, int(v_h * 0.1))
        
        col3, col4 = st.columns(2)
        w_width = col3.slider("W", 10, v_w - w_x, min(150, v_w - w_x))
        w_height = col4.slider("H", 10, v_h - w_y, min(80, v_h - w_y))
        
        if st.button("🚫 ERASE"):
            with tempfile.TemporaryDirectory() as tmp_dir:
                v_in = os.path.join(tmp_dir, "i.mp4")
                v_out = os.path.join(tmp_dir, "o.mp4")
                with open(v_in, "wb") as f: 
                    f.write(wm_vid.getbuffer())
                    
                cap = cv2.VideoCapture(v_in)
                writer = cv2.VideoWriter(v_out + "_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), (v_w, v_h))
                tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                f_idx = 0
                p_bar = st.progress(0)
                
                while True:
                    success, frame = cap.read()
                    if not success: 
                        break
                    roi = frame[w_y:w_y+w_height, w_x:w_x+w_width]
                    if roi.size != 0: 
                        frame[w_y:w_y+w_height, w_x:w_x+w_width] = cv2.GaussianBlur(roi, (61, 61), 0)
                    writer.write(frame)
                    f_idx += 1
                    if f_idx % 30 == 0: 
                        p_bar.progress(min(f_idx/tot_frames, 1.0))
                        
                cap.release()
                writer.release()
                
                with VideoFileClip(v_in) as o_vid:
                    with VideoFileClip(v_out + "_t.mp4") as p_vid: 
                        final_clip = p_vid.set_audio(o_vid.audio)
                        final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                        
                st.success("✅ FIXED!")
                st.video(v_out)
                with open(v_out, "rb") as o_f: 
                    st.download_button("📥 DOWNLOAD", o_f, "wdpro_wm.mp4")

# ------------------------------------------------------------------------------------------
# TAB 4: CINEMATIC GRADING
# ------------------------------------------------------------------------------------------
with tab_pro:
    st.markdown("<h2 style='color:#d2691e;'>✨ Cinematic Grading</h2>", unsafe_allow_html=True)
    pro_vid = st.file_uploader("Upload Clip", type=["mp4", "mov"], key="pro_up")
    grade_mode = st.radio("Mode:", ["🤖 AI Presets", "🎛️ Manual"], horizontal=True)
    
    if "Presets" in grade_mode:
        chosen_preset = st.selectbox("Filter (100)", list(CINEMATIC_FILTERS_100.keys()))
        b_val, c_val, s_val, w_val = CINEMATIC_FILTERS_100[chosen_preset]
    else:
        colA, colB = st.columns(2)
        b_val = colA.slider("☀️ Brightness", 0.3, 2.0, 1.0)
        c_val = colB.slider("🌗 Contrast", 0.3, 2.0, 1.0)
        colC, colD = st.columns(2)
        s_val = colC.slider("🌈 Saturation", 0.0, 3.0, 1.0)
        w_val = colD.slider("🔥 Warmth", -50, 50, 0)
        
    if pro_vid and st.button("✨ RENDER"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in = os.path.join(tmp_dir, "i.mp4")
            v_out = os.path.join(tmp_dir, "o.mp4")
            with open(v_in, "wb") as f: 
                f.write(pro_vid.getbuffer())
                
            cap = cv2.VideoCapture(v_in)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), (w, h))
            
            tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            f_idx = 0
            p_bar = st.progress(0)
            
            while True:
                success, frame = cap.read()
                if not success: 
                    break
                frame = master_color_grader_pil(frame, b_val, c_val, s_val, w_val)
                writer.write(frame)
                f_idx += 1
                if f_idx % 20 == 0: 
                    p_bar.progress(min(f_idx/tot_frames, 1.0))
                    
            cap.release()
            writer.release()
            
            with VideoFileClip(v_in) as o_vid:
                with VideoFileClip(v_out + "_t.mp4") as p_vid: 
                    final_clip = p_vid.set_audio(o_vid.audio)
                    final_clip.write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                    
            st.success("✅ CINEMATIC!")
            st.video(v_out)
            with open(v_out, "rb") as o_f: 
                st.download_button("📥 DOWNLOAD", o_f, "wdpro_graded.mp4")
        
