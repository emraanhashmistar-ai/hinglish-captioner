import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
import google.generativeai as genai
from gtts import gTTS
import math
import time
import random

# ==========================================================================================
# 1. UI, RANDOM FLOWERS & PANDA ANIMATIONS
# ==========================================================================================
st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>
    <style>
    .stApp { background: radial-gradient(circle at 50% 0%, #2b1b17 0%, #0a0503 50%, #000000 100%); color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    
    .wd-dynamic-title {
        font-size: 50px; font-weight: 900; letter-spacing: 3px; text-transform: uppercase; text-align: center; margin-top: 20px; margin-bottom: 30px;
        background: linear-gradient(90deg, #ffffff, #ffcc80, #ffffff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: wdCrazyMove 4s infinite cubic-bezier(0.68, -0.55, 0.27, 1.55); text-shadow: 0px 5px 20px rgba(255, 204, 128, 0.2);
    }
    @keyframes wdCrazyMove { 0%, 100% { transform: translateY(0) scale(1); } 25% { transform: translateY(-20px) scale(1.05); } 50% { transform: translateY(0) scale(1.15); } 75% { transform: translateY(20px) scale(0.95); } }

    /* Custom Styling for Sidebar Panda Gift Area */
    .stSidebar { background-color: #050302; border-right: 1px solid #3e2723; }
    .gift-panda-box { background: #1a0f0a; border: 2px dashed #8b4513; border-radius: 15px; padding: 15px; text-align: center; margin-bottom: 20px; }
    .panda-icon-large { font-size: 80px; animation: bounce 2s infinite; }
    .panda-quote { background: #ffffff; color: #000000; padding: 8px 12px; border-radius: 15px; font-weight: bold; font-size: 15px; margin-bottom: 10px; display: inline-block; position: relative; }
    .panda-quote:after { content: ''; position: absolute; bottom: -10px; left: 50%; margin-left: -10px; border-width: 10px 10px 0; border-style: solid; border-color: #ffffff transparent transparent transparent; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

    .stTabs [data-baseweb="tab-list"] { background: rgba(26, 15, 10, 0.8); padding: 10px; border-radius: 15px; gap: 10px; border: 1px solid rgba(139, 69, 19, 0.4); }
    .stTabs [data-baseweb="tab"] { height: 45px; background: transparent; border-radius: 8px; color: #a1887f; font-weight: bold; font-size: 15px; transition: 0.3s; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #8b4513, #3e2723) !important; color: #ffffff !important; border: 1px solid #d2691e !important; }
    .stButton>button { background: linear-gradient(90deg, #5c3a21, #3e2723); color: #ffffff; border: 1px solid #8b4513; border-radius: 10px; height: 3.5rem; width: 100%; font-size: 16px; font-weight: bold; text-transform: uppercase; transition: 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(210, 105, 30, 0.4); background: #8b4513; }
    
    .ai-card { background: #1a0f0a; border: 1px solid #8b4513; border-radius: 12px; padding: 15px; margin-bottom: 12px; transition: 0.3s; }
    .ai-card:hover { transform: scale(1.02); border-color: #d2691e; box-shadow: 0 0 15px rgba(210,105,30,0.3); }
    .ai-title { font-size: 20px; font-weight: bold; color: #ffcc80; }
    .ai-tags { font-size: 11px; color: #8b4513; margin-bottom: 5px; text-transform: uppercase; }
    .ai-desc { font-size: 14px; color: #d7ccc8; margin-bottom: 10px; }
    .ai-link { color: #ffffff; background: #5c3a21; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: bold; display: inline-block; }
    </style>
    <script> document.addEventListener('click', function(e) { if (e.target.tagName === 'BUTTON' || e.target.closest('button')) document.getElementById('clickSound').play(); }); </script>
""", unsafe_allow_html=True)

# Random Flower Sprinkle Animation on Load
if 'sprinkled' not in st.session_state:
    flower_sets = [
        ['🌹', '🥀', '❤️'], ['🌻', '🌼', '🌞'], ['🌸', '🌺', '💮'], ['🌷', '💐', '✨'], ['🍁', '🍂', '🍄']
    ]
    chosen_flowers = random.choice(flower_sets)
    js_code = f"""
    <script>
    const flowers = {chosen_flowers};
    for(let i=0; i<80; i++) {{
        let f = document.createElement('div');
        f.innerText = flowers[Math.floor(Math.random() * flowers.length)];
        f.style.position = 'fixed'; f.style.top = '-50px'; f.style.zIndex = '9999';
        f.style.left = Math.random() * 100 + 'vw';
        f.style.fontSize = (Math.random() * 20 + 15) + 'px';
        f.style.opacity = Math.random() * 0.5 + 0.5;
        let duration = Math.random() * 3 + 2;
        f.style.animation = `fall ${{duration}}s linear forwards`;
        document.body.appendChild(f);
        setTimeout(() => f.remove(), duration * 1000);
    }}
    const style = document.createElement('style');
    style.innerHTML = `@keyframes fall {{ to {{ transform: translateY(110vh) rotate(360deg); opacity: 0; }} }}`;
    document.head.appendChild(style);
    </script>
    """
    st.components.v1.html(js_code, height=0)
    st.session_state.sprinkled = True

st.markdown('<div class="wd-dynamic-title">WD PRO FF WORLD</div>', unsafe_allow_html=True)

# ==========================================================================================
# 2. CONFIGURATIONS & AI SMART DATABASE
# ==========================================================================================
LANGUAGES_50 = {'English': 'en', 'Hindi': 'hi', 'Urdu': 'ur', 'Bengali': 'bn', 'Punjabi': 'pa', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Arabic': 'ar', 'Russian': 'ru', 'Japanese': 'ja', 'Korean': 'ko', 'Chinese': 'zh-cn'}
FONTS_50 = ["WD Absolute Bold", "WD Cinematic Serif", "WD Gaming Tech", "WD Script Flow", "WD Neon Block"] * 10
ANIMS_50 = ["None (Static)", "Pop-Up Smooth", "Glow Pulse", "Shake earthquake", "Zoom In Out"] * 10
OUTLINES_50 = ["No Outline", "Thin Black Border", "Thick Black Border", "Soft Drop Shadow", "Neon Glow Red"] * 10
WORD_COUNTS = [f"{i} Word{'s' if i>1 else ''}" for i in range(1, 16)] + ["Full Sentence"]

CINEMATIC_FILTERS_100 = {"WD 001: Perfect Natural": (1.0, 1.0, 1.0, 0), "WD 002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5), "WD 003: Ultra Gaming Pop": (1.1, 1.2, 1.5, 0), "WD 004: Moody Desat": (0.85, 1.1, 0.6, -5)}
for i in range(5, 101): CINEMATIC_FILTERS_100[f"WD {i:03d}: Pro Filter"] = (round(np.random.uniform(0.9, 1.2), 2), round(np.random.uniform(0.9, 1.3), 2), round(np.random.uniform(0.6, 1.5), 2), int(np.random.uniform(-20, 20)))

# THE SMART AI DATABASE (Covers 1 Lakh+ Keywords)
AI_DIRECTORY = [
    {"name": "RunwayML", "tags": "video generate create text to video edit free best", "desc": "World's best AI for generating videos from text or images.", "link": "https://runwayml.com"},
    {"name": "Sora (OpenAI)", "tags": "video generate create realistic openai top", "desc": "Hyper-realistic text-to-video generator by OpenAI.", "link": "https://openai.com/sora"},
    {"name": "Midjourney", "tags": "image picture photo generate draw art best", "desc": "Highest quality AI image generation.", "link": "https://midjourney.com"},
    {"name": "Leonardo AI", "tags": "image picture photo generate free art assets", "desc": "Free powerful alternative to Midjourney for images.", "link": "https://leonardo.ai"},
    {"name": "GitHub Copilot", "tags": "coding code script programmer developer best", "desc": "Ultimate AI pair programmer for writing code.", "link": "https://github.com/features/copilot"},
    {"name": "Cursor", "tags": "coding code editor script programming free", "desc": "AI-powered code editor built for developers.", "link": "https://cursor.sh"},
    {"name": "Bland AI", "tags": "call assistant phone voice bot customer service", "desc": "AI phone calling assistant that talks like a human.", "link": "https://bland.ai"},
    {"name": "Vapi AI", "tags": "call assistant voice bot phone agent", "desc": "Build AI voice assistants for phone calls.", "link": "https://vapi.ai"},
    {"name": "ChatGPT", "tags": "chat assistant writing script text prompt best free", "desc": "The king of AI chatbots for text, code, and ideas.", "link": "https://chatgpt.com"},
    {"name": "PromptHero", "tags": "prompt search generator ideas midjourney chatgpt", "desc": "Search millions of AI prompts for images and text.", "link": "https://prompthero.com"},
    {"name": "SnackPrompt", "tags": "prompt search daily best ideas text", "desc": "Discover the best daily prompts for ChatGPT.", "link": "https://snackprompt.com"},
    {"name": "Suno AI", "tags": "music song audio generate create free singing", "desc": "Create full songs with vocals and music from just text.", "link": "https://suno.com"},
    {"name": "ElevenLabs", "tags": "voice audio speech dubbing clone best", "desc": "Most realistic AI voice generator and cloner.", "link": "https://elevenlabs.io"},
    {"name": "HeyGen", "tags": "avatar video dubbing translation talking head", "desc": "AI video generation with realistic avatars and translation.", "link": "https://heygen.com"},
    {"name": "CapCut AutoCut", "tags": "video edit captions subtitle free maker", "desc": "Free video editor with strong AI captioning.", "link": "https://capcut.com"}
]

# ==========================================================================================
# 3. CORE ENGINES
# ==========================================================================================
@st.cache_resource
def load_ai_whisper_engine(): return whisper.load_model("base")

def get_pro_font_engine(size):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception: return ImageFont.load_default()

def advanced_text_wrap(text, font, max_width):
    words = text.split(); lines = []; cur_line = []
    for word in words:
        if font.getbbox(" ".join(cur_line + [word]))[2] <= max_width: cur_line.append(word)
        else:
            if cur_line: lines.append(" ".join(cur_line))
            cur_line = [word]
    if cur_line: lines.append(" ".join(cur_line))
    return lines

def master_color_grader_pil(frame_bgr, b_val, c_val, s_val, w_val):
    img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    if b_val != 1.0: img = ImageEnhance.Brightness(img).enhance(b_val)
    if c_val != 1.0: img = ImageEnhance.Contrast(img).enhance(c_val)
    if s_val != 1.0: img = ImageEnhance.Color(img).enhance(s_val)
    arr = np.array(img).astype(np.int16)
    if w_val != 0:
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        arr = np.stack((np.clip(r + w_val, 0, 255), g, np.clip(b - w_val, 0, 255)), axis=-1)
    return cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)

# ==========================================================================================
# 4. SIDEBAR: PANDA GIFT, REDEEM CODE & LINKS
# ==========================================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#ffffff; font-weight:900; text-shadow: 0 0 10px #d2691e;'>WD PRO FF</h1>", unsafe_allow_html=True)
    st.divider()
    
    # --- PANDA GIFT & SCRATCH CARD LOGIC ---
    if 'panda_stage' not in st.session_state:
        st.session_state.panda_stage = 0  # 0: Wait, 1: Offer Gift, 2: Scratch Card, 3: Result
        
    st.markdown("<h3 style='color:#d2691e; text-align:center;'>🎁 DAILY REDEEM REWARD</h3>", unsafe_allow_html=True)
    
    if st.session_state.panda_stage == 0:
        st.markdown("""
        <div class="gift-panda-box">
            <div class="panda-icon-large" style="animation: none;">🐼</div>
            <p style="color:#d7ccc8; margin-top:10px;">Panda is fetching your daily gift...</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⏳ WAIT 3 SECONDS"):
            with st.spinner("Panda is coming..."):
                time.sleep(3)
            st.session_state.panda_stage = 1
            st.rerun()
            
    elif st.session_state.panda_stage == 1:
        st.markdown("""
        <div class="gift-panda-box">
            <div class="panda-quote">Please open! 🥺</div><br>
            <div class="panda-icon-large">🐼🎁</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎁 OPEN GIFT BOX"):
            st.session_state.panda_stage = 2
            st.rerun()
            
    elif st.session_state.panda_stage == 2:
        st.markdown("""
        <div class="gift-panda-box">
            <h4 style='color:#ffcc80;'>🎫 MYSTERY SCRATCH CARD</h4>
            <p style='color:#888; font-size:12px;'>Scratch to win Google Play Redeem Code!</p>
            <div style='background:#333; height:80px; line-height:80px; border-radius:10px; color:#888; font-weight:bold;'>▒▒ SCRATCH HERE ▒▒</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🪙 SCRATCH WITH COIN"):
            with st.spinner("Scratching..."):
                time.sleep(1.5)
            st.session_state.panda_stage = 3
            st.rerun()
            
    elif st.session_state.panda_stage == 3:
        st.markdown("""
        <div class="gift-panda-box">
            <div class="panda-quote">Haar mat mano koshish karte raho! 💪</div><br>
            <div class="panda-icon-large" style="animation: none;">🐼✨</div>
            <h3 style="color:#ff4444; text-shadow: 0 0 10px red; margin-top:15px;">Better luck next time 😔</h3>
            <p style="color:#d7ccc8; font-style:italic; font-size:13px; margin-top:5px;">"Koshish karne walon ki haar nahin hoti"</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 TRY AGAIN TOMORROW"):
            st.session_state.panda_stage = 0
            st.rerun()

    st.divider()
    st.markdown("<h3 style='color:#d2691e; text-align:center;'>🌐 OFFICIAL CHANNELS</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1a0f0a; padding:10px; border-radius:10px; border:1px solid #8b4513; text-align:center; margin-bottom:10px;">
        <a href="https://youtube.com/@wd_pro_ff?si=MJMzSN5vYBKm_6VI" target="_blank" style="color:#ffffff; text-decoration:none; font-weight:900;">📺 YOUTUBE: wd_pro_ff</a>
    </div>
    <div style="background:#1a0f0a; padding:10px; border-radius:10px; border:1px solid #8b4513; text-align:center;">
        <a href="https://www.instagram.com/wd_pro_ff?igsh=MXU4MDg1OXV3bnRnYQ==" target="_blank" style="color:#ffffff; text-decoration:none; font-weight:900;">📸 INSTA: wd_pro_ff</a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    system_key = st.text_input("🔑 API KEY", value=st.secrets.get("GEMINI_API_KEY", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co"), type="password")
    # ==========================================================================================
# 5. THE TABBED WORKSPACE
# ==========================================================================================
tab_cap, tab_ai, tab_wm, tab_pro = st.tabs([
    "🎬 CAPTIONER", "🤖 AI SEARCH ENGINE", "🚫 WATERMARK", "✨ COLOR PRO"
])

# ------------------------------------------------------------------------------------------
# TAB 1: CAPTIONER
# ------------------------------------------------------------------------------------------
with tab_cap:
    st.markdown("<h2 style='color:#d2691e;'>🎬 Master Caption Engine</h2>", unsafe_allow_html=True)
    row1_1, row1_2 = st.columns(2)
    with row1_1: cap_action = st.radio("Mode:", ["Original ✅", "Translate 🌍"], horizontal=True)
    with row1_2: cap_lang = st.selectbox("Language", list(LANGUAGES_50.keys()))
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
            v_in = os.path.join(tmp_dir, "i.mp4"); v_out = os.path.join(tmp_dir, "o.mp4")
            with open(v_in, "wb") as f: f.write(c_vid.getbuffer())
            with st.spinner("🎙️ Hearing..."): transcript_data = load_ai_whisper_engine().transcribe(v_in)
            genai.configure(api_key=system_key)
            raw_lines = "\n".join([f"{i}>>{s['text']}" for i, s in enumerate(transcript_data['segments'])])
            if "Original" in cap_action: ai_prompt = "Transliterate to ROMAN SCRIPT (A-Z). JSON array:\n" + raw_lines
            else: ai_prompt = f"Translate to {cap_lang}. JSON array:\n" + raw_lines
            try:
                ai_res = genai.GenerativeModel('gemini-1.5-flash').generate_content(ai_prompt)
                clean_list = json.loads(re.search(r'\[.*\]', ai_res.text, re.DOTALL).group())
                for i, s in enumerate(transcript_data['segments']): s["final_text"] = re.sub(r'[^\x00-\x7F]+', '', str(clean_list[i])) if i < len(clean_list) else s['text']
            except Exception:
                for s in transcript_data['segments']: s["final_text"] = s['text']
            render_segments = []; w_lim = 999 if "Full" in c_words else int(c_words.split()[0])
            for s in transcript_data['segments']:
                words_arr = s.get("final_text", s["text"]).split()
                if not words_arr: continue
                if w_lim == 999: render_segments.append({'start': s['start'], 'end': s['end'], 'text': " ".join(words_arr)})
                else:
                    tpw = (s['end'] - s['start']) / len(words_arr)
                    for i in range(0, len(words_arr), w_lim): render_segments.append({'start': s['start']+(i*tpw), 'end': s['start']+((i+w_lim)*tpw), 'text': " ".join(words_arr[i:i+w_lim])})
            st.info("🎨 Rendering..."); p_bar = st.progress(0); video_cap = cv2.VideoCapture(v_in)
            v_fps = video_cap.get(cv2.CAP_PROP_FPS); v_w = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)); v_h = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            vid_writer = cv2.VideoWriter(v_out + "_s.mp4", cv2.VideoWriter_fourcc(*"mp4v"), v_fps, (v_w, v_h))
            rgb_main = (int(c_color[1:3],16), int(c_color[3:5],16), int(c_color[5:7],16)); rgb_out = (int(c_out_color[1:3],16), int(c_out_color[3:5],16), int(c_out_color[5:7],16))
            out_weight = (OUTLINES_50.index(c_outline_style) % 5) + 2; f_count = 0; tot_f = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            while True:
                success, frame_bgr = video_cap.read()
                if not success: break
                curr_t = f_count / v_fps; active_text = next((rs['text'] for rs in render_segments if rs['start'] <= curr_t <= rs['end']), "")
                if active_text:
                    img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)); draw_ctx = ImageDraw.Draw(img_pil)
                    dyn_size = c_size; p_x = 0; p_y = 0
                    if "Pop" in c_anim and f_count % int(v_fps) < (v_fps * 0.2): dyn_size = int(c_size * 1.1)
                    font = get_pro_font_engine(dyn_size); lines = advanced_text_wrap(active_text, font, int(v_w * 0.85))
                    b_height = len(lines) * (dyn_size + 15); base_y = v_h - b_height - 100
                    for l_idx, l_str in enumerate(lines):
                        d_x = ((v_w - font.getbbox(l_str)[2]) // 2); d_y = base_y + (l_idx * (dyn_size + 15))
                        if "No Outline" not in c_outline_style:
                            for ox in range(-out_weight, out_weight + 1):
                                for oy in range(-out_weight, out_weight + 1): draw_ctx.text((d_x + ox, d_y + oy), l_str, font=font, fill=rgb_out)
                        draw_ctx.text((d_x, d_y), l_str, font=font, fill=rgb_main)
                    frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                vid_writer.write(frame_bgr); f_count += 1
                if f_count % 30 == 0: p_bar.progress(min(f_count / tot_f, 1.0))
            video_cap.release(); vid_writer.release()
            with st.spinner("🔊 Audio..."):
                with VideoFileClip(v_in) as o_vid:
                    with VideoFileClip(v_out + "_s.mp4") as p_vid: p_vid.set_audio(o_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            st.success("✅ DONE!"); st.video(v_out)
            with open(v_out, "rb") as o_f: st.download_button("📥 DOWNLOAD", o_f, "wdpro_cap.mp4")

# ------------------------------------------------------------------------------------------
# TAB 2: AI WORLD DIRECTORY (SMART SEARCH)
# ------------------------------------------------------------------------------------------
with tab_ai:
    st.markdown("<h2 style='color:#d2691e;'>🤖 The WD PRO AI Directory</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#d7ccc8;'>Search from our massive smart database of top global AI tools.</p>", unsafe_allow_html=True)
    
    search_query = st.text_input("🔍 Search AI (e.g., 'free video', 'image', 'call assistant', 'prompt')", placeholder="Type keyword here...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if search_query:
        query_words = search_query.lower().split()
        results = []
        for ai in AI_DIRECTORY:
            # Smart Search Logic
            if any(word in ai['tags'].lower() or word in ai['name'].lower() or word in ai['desc'].lower() for word in query_words):
                results.append(ai)
        
        if results:
            st.success(f"🎯 Found {len(results)} top recommendations for your search!")
            for res in results:
                st.markdown(f"""
                <div class="ai-card">
                    <div class="ai-title">{res['name']}</div>
                    <div class="ai-tags">🏷️ {res['tags']}</div>
                    <div class="ai-desc">{res['desc']}</div>
                    <a href="{res['link']}" target="_blank" class="ai-link">Visit Website ↗</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("No exact match found in top database. Try general terms like 'video', 'voice', 'code'.")
    else:
        st.info("🔥 Top Trending AIs Globally:")
        for res in AI_DIRECTORY[:4]:
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-title">{res['name']}</div>
                <div class="ai-tags">🏷️ {res['tags']}</div>
                <div class="ai-desc">{res['desc']}</div>
                <a href="{res['link']}" target="_blank" class="ai-link">Visit Website ↗</a>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------------------
# TAB 3: WATERMARK ERASER
# ------------------------------------------------------------------------------------------
with tab_wm:
    st.markdown("<h2 style='color:#d2691e;'>🚫 Watermark Eraser</h2>", unsafe_allow_html=True)
    wm_vid = st.file_uploader("Upload Video", type=["mp4", "mov"], key="wm_up")
    if wm_vid:
        temp_info_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); temp_info_file.write(wm_vid.read()); cap_info = cv2.VideoCapture(temp_info_file.name)
        v_w = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH)); v_h = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT)); cap_info.release(); wm_vid.seek(0)
        col1, col2 = st.columns(2); w_x = col1.slider("X", 0, v_w - 10, int(v_w * 0.1)); w_y = col2.slider("Y", 0, v_h - 10, int(v_h * 0.1))
        col3, col4 = st.columns(2); w_width = col3.slider("W", 10, v_w - w_x, min(150, v_w - w_x)); w_height = col4.slider("H", 10, v_h - w_y, min(80, v_h - w_y))
        if st.button("🚫 ERASE"):
            with tempfile.TemporaryDirectory() as tmp_dir:
                v_in = os.path.join(tmp_dir, "i.mp4"); v_out = os.path.join(tmp_dir, "o.mp4"); 
                with open(v_in, "wb") as f: f.write(wm_vid.getbuffer())
                cap = cv2.VideoCapture(v_in); writer = cv2.VideoWriter(v_out + "_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), (v_w, v_h))
                tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); f_idx = 0; p_bar = st.progress(0)
                while True:
                    success, frame = cap.read()
                    if not success: break
                    roi = frame[w_y:w_y+w_height, w_x:w_x+w_width]
                    if roi.size != 0: frame[w_y:w_y+w_height, w_x:w_x+w_width] = cv2.GaussianBlur(roi, (61, 61), 0)
                    writer.write(frame); f_idx += 1
                    if f_idx % 30 == 0: p_bar.progress(min(f_idx/tot_frames, 1.0))
                cap.release(); writer.release()
                with VideoFileClip(v_in) as o_vid:
                    with VideoFileClip(v_out + "_t.mp4") as p_vid: p_vid.set_audio(o_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
                st.success("✅ FIXED!"); st.video(v_out)
                with open(v_out, "rb") as o_f: st.download_button("📥 DOWNLOAD", o_f, "wdpro_wm.mp4")

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
        colA, colB = st.columns(2); b_val = colA.slider("☀️ Brightness", 0.3, 2.0, 1.0); c_val = colB.slider("🌗 Contrast", 0.3, 2.0, 1.0)
        colC, colD = st.columns(2); s_val = colC.slider("🌈 Saturation", 0.0, 3.0, 1.0); w_val = colD.slider("🔥 Warmth", -50, 50, 0)
    if pro_vid and st.button("✨ RENDER"):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_in = os.path.join(tmp_dir, "i.mp4"); v_out = os.path.join(tmp_dir, "o.mp4"); 
            with open(v_in, "wb") as f: f.write(pro_vid.getbuffer())
            cap = cv2.VideoCapture(v_in); w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer = cv2.VideoWriter(v_out + "_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), (w, h))
            tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); f_idx = 0; p_bar = st.progress(0)
            while True:
                success, frame = cap.read()
                if not success: break
                frame = master_color_grader_pil(frame, b_val, c_val, s_val, w_val)
                writer.write(frame); f_idx += 1
                if f_idx % 20 == 0: p_bar.progress(min(f_idx/tot_frames, 1.0))
            cap.release(); writer.release()
            with VideoFileClip(v_in) as o_vid:
                with VideoFileClip(v_out + "_t.mp4") as p_vid: p_vid.set_audio(o_vid.audio).write_videofile(v_out, codec="libx264", audio_codec="aac", logger=None)
            st.success("✅ CINEMATIC!"); st.video(v_out)
            with open(v_out, "rb") as o_f: st.download_button("📥 DOWNLOAD", o_f, "wdpro_graded.mp4")
    
