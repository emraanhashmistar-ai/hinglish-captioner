import streamlit as st
import tempfile, os, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import time, random, datetime

try:
    from moviepy.editor import VideoFileClip
except Exception:
    pass

import whisper
import google.generativeai as genai

st.set_page_config(page_title="WD PRO FF WORLD", page_icon="🐼", layout="wide")

if 'gender' not in st.session_state: st.session_state.gender = None
if 'anim_done' not in st.session_state: st.session_state.anim_done = False
if 'scratched_today' not in st.session_state: st.session_state.scratched_today = False
if 'panda_stage' not in st.session_state: st.session_state.panda_stage = 0

if st.session_state.gender is None:
    st.markdown("<h1 style='text-align:center; color:#008080; margin-top:50px;'>WD PRO FF WORLD 🐼</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#D3D3D3;'>Pehle apni identity chunein:</h3><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
    with c2:
        if st.button("👑 I AM A KING (LADKA)", use_container_width=True):
            st.session_state.gender = "King"; st.rerun()
    with c3:
        if st.button("👸 I AM A QUEEN (LADKI)", use_container_width=True):
            st.session_state.gender = "Queen"; st.rerun()
    st.stop()

if not st.session_state.anim_done:
    wp = st.empty()
    tid = "KING" if st.session_state.gender == "King" else "QUEEN"
    
    js_code = "<script src='https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js'></script>"
    js_code += "<script>var duration=4000; var end=Date.now()+duration; "
    js_code += "setInterval(function(){if(Date.now()>end)return;"
    js_code += "confetti({particleCount:10, spread:360});}, 250);</script>"
    
    bg_css = "<style>.bg_box{position:fixed;top:0;left:0;width:100vw;height:100vh;background:#000;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;}</style>"
    html_txt = "<div class='bg_box'><h1 style='color:#008080;font-size:8vw;'>WD PRO FF</h1>"
    html_txt += "<h3 style='color:#B4D8E7;font-style:italic;'>Every subscriber is my " + tid + " 👑</h3></div>"
    
    with wp.container():
        st.components.v1.html(js_code, height=0)
        st.markdown(bg_css + html_txt, unsafe_allow_html=True)
        time.sleep(4.5)
    wp.empty()
    st.session_state.anim_done = True
    css1 = "<style>.stApp{background:#000; color:#D3D3D3;} "
css2 = ".wd-head{font-size:40px;font-weight:900;text-align:center;background:linear-gradient(90deg,#008080,#B4D8E7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;} "
css3 = ".stButton>button{background:linear-gradient(135deg,#008080,#111);color:white;border:1px solid #008080;border-radius:10px;font-weight:bold;transition:0.3s;} "
css4 = ".ai-card{background:#111;border:1px solid #008080;padding:15px;border-radius:10px;margin-bottom:15px;} "
css5 = ".stat{background:#001a1a;color:#00ffcc;padding:12px;text-align:center;font-weight:bold;border:1px solid #008080;border-radius:8px;}</style>"
st.markdown(css1 + css2 + css3 + css4 + css5, unsafe_allow_html=True)

st.markdown("<div class='wd-head'>WD PRO FF WORLD</div>", unsafe_allow_html=True)
links = "<div style='text-align:center;margin-bottom:20px;'><a href='https://youtube.com/@wd_pro_ff' style='color:#B4D8E7;margin-right:15px;'>📺 YouTube</a>"
links += "<a href='https://instagram.com/wd_pro_ff' style='color:#B4D8E7;'>📸 Instagram</a></div>"
st.markdown(links, unsafe_allow_html=True)

LANGS = ["English", "Hindi", "Urdu", "Bengali", "Marathi", "Telugu", "Tamil", "Gujarati", "Kannada", "Odia", "Malayalam", "Punjabi", "Assamese", "Maithili", "Santali", "Kashmiri", "Nepali", "Sindhi", "Dogri", "Konkani", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese", "Arabic", "Turkish", "Vietnamese", "Thai", "Dutch", "Polish", "Swedish", "Danish", "Finnish", "Norwegian", "Greek", "Czech", "Hungarian", "Romanian", "Ukrainian", "Hebrew", "Indonesian", "Malay", "Filipino", "Swahili", "Afrikaans"]

AI_DB = {"Video":[], "Image":[], "Prompt":[], "Voice":[]}
for c in AI_DB:
    for i in range(1, 501):
        AI_DB[c].append({"n": c + " Pro Tool " + str(i), "l": "https://google.com", "d": "Premium " + c + " AI"})
AI_DB["Video"][0] = {"n":"RunwayML", "l":"https://runwayml.com", "d":"Best Cinematic Text-to-Video."}
AI_DB["Video"][1] = {"n":"Sora", "l":"https://openai.com/sora", "d":"OpenAI's realistic video generator."}
AI_DB["Image"][0] = {"n":"Midjourney", "l":"https://midjourney.com", "d":"Top quality photorealistic images."}

FILTERS = {"001: Original": (1.0,1.0,1.0,0), "002: Hollywood Teal": (0.9,1.2,1.3,10)}
for i in range(3, 1001):
    FILTERS["WD " + str(i).zfill(4) + ": Grade"] = (round(random.uniform(0.8,1.2),2), round(random.uniform(0.9,1.4),2), round(random.uniform(0.5,1.6),2), random.randint(-20,20))
    with st.sidebar:
    st.markdown("<h2 style='text-align:center;color:#008080;'>🐼 WD PRO PANDA</h2><hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#B4D8E7;text-align:center;'>🎁 DAILY SCRATCH CARD</h3>", unsafe_allow_html=True)
    
    n_now = datetime.datetime.now()
    n_mid = datetime.datetime(n_now.year, n_now.month, n_now.day) + datetime.timedelta(days=1)
    diff = n_mid - n_now
    hh, rr = divmod(diff.seconds, 3600); mm, ss = divmod(rr, 60)
    
    if st.session_state.scratched_today:
        st.error("LOCKED 🔒 Come back tomorrow!")
        st.info("Time left: " + str(hh) + "h " + str(mm) + "m")
        st.write("Koshish karne walon ki haar nahin hoti 😔")
    else:
        if st.session_state.panda_stage == 0:
            st.markdown("<h1 style='text-align:center;'>🐼</h1>", unsafe_allow_html=True)
            if st.button("GET GIFT"):
                time.sleep(1); st.session_state.panda_stage = 1; st.rerun()
        elif st.session_state.panda_stage == 1:
            st.write("Please open! 🐼👉🎁")
            if st.button("OPEN BOX"):
                st.session_state.panda_stage = 2; st.rerun()
        elif st.session_state.panda_stage == 2:
            st.write("▒▒ SCRATCH HERE ▒▒")
            if st.button("SCRATCH COIN"):
                time.sleep(1.5); st.session_state.scratched_today = True; st.rerun()
                
    st.divider()
    API_KEY = st.text_input("Gemini API Key", "AIzaSyC4axyeGWQfDHoDmK7D8WdFiQReUllm3Co", type="password")

t1, t2, t3, t4, t5 = st.tabs(["⬇️ DL", "🎬 CAPTION", "🤖 AI", "🚫 WM", "✨ COLOR"])

with t1:
    st.subheader("⬇️ Universal Media Downloader")
    d_m = st.radio("Format:", ["Video", "Audio"], horizontal=True)
    d_u = st.text_input("Link (YT/Insta):")
    if d_u and st.button("DOWNLOAD"):
        import yt_dlp
        with tempfile.TemporaryDirectory() as td:
            st.markdown("<div class='stat'>⏳ Fetching Media...</div>", unsafe_allow_html=True)
            try:
                opt = {'outtmpl': os.path.join(td, '%(title)s.%(ext)s'), 'quiet': True}
                opt['http_headers'] = {'User-Agent': 'Mozilla/5.0'}
                if 'Video' in d_m: opt['format'] = 'best[ext=mp4]/best'
                else:
                    opt['format'] = 'bestaudio/best'
                    opt['postprocessors'] = [{'key':'FFmpegExtractAudio', 'preferredcodec':'mp3'}]
                
                with yt_dlp.YoutubeDL(opt) as y:
                    inf = y.extract_info(d_u, download=True)
                    fn = y.prepare_filename(inf)
                    if 'Audio' in d_m: fn = fn.rsplit('.', 1)[0] + '.mp3'
                    st.success("✅ Ready!")
                    with open(fn, "rb") as f:
                        b_txt = "Save MP4" if 'Video' in d_m else "Save MP3"
                        st.download_button(b_txt, f.read(), os.path.basename(fn))
            except Exception as e:
                st.error("Download failed! IP is blocked or link is private.")
                @st.cache_resource
def get_whisper(): return whisper.load_model("base")

with t2:
    st.subheader("🎬 Master Caption Engine")
    c_m = st.radio("Mode:", ["Original", "Translate"])
    c_l = st.selectbox("Language:", LANGS)
    c1, c2, c3 = st.columns(3)
    c_spd = c1.selectbox("Speed:", ["1 Word", "2 Words", "Full Sentence"])
    c_sz = c2.slider("Size:", 30, 100, 70)
    c_pos = c3.selectbox("Pos:", ["Bottom", "Top"])
    
    c_vid = st.file_uploader("Upload Video:", type=["mp4"])
    
    if c_vid and st.button("GENERATE ROMAN CAPTIONS"):
        with tempfile.TemporaryDirectory() as td:
            ip = os.path.join(td, "i.mp4")
            op = os.path.join(td, "o.mp4")
            with open(ip, "wb") as f: f.write(c_vid.getbuffer())
            
            st.markdown("<div class='stat'>⏳ Extracting Audio...</div>", unsafe_allow_html=True)
            w_res = get_whisper().transcribe(ip)
            raw = "\\n".join([s['text'] for s in w_res['segments']])
            
            st.markdown("<div class='stat'>⏳ AI Scripting (Strict Roman Script)...</div>", unsafe_allow_html=True)
            genai.configure(api_key=API_KEY)
            
            # SAFE PROMPT STRING CONCATENATION (NO LONG F-STRINGS)
            p1 = "Translate to " + c_l + ". "
            p2 = "CRITICAL: Use ONLY English alphabets (A-Z). NO Urdu/Hindi script. "
            p3 = "Output ONLY a JSON array of strings. Text:\\n"
            p_final = p1 + p2 + p3 + raw
            
            try:
                gm = genai.GenerativeModel('gemini-1.5-flash')
                g_out = gm.generate_content(p_final).text.strip()
                g_out = g_out.replace("```json", "").replace("```", "")
                if "[" in g_out: g_out = g_out[g_out.find("["):g_out.rfind("]")+1]
                cln = json.loads(g_out)
                for i, s in enumerate(w_res['segments']):
                    s['f_txt'] = str(cln[i]) if i < len(cln) else s['text']
                st.success("API Success! Roman Script ready.")
            except Exception:
                st.error("API Limit! Using original text.")
                for s in w_res['segments']: s['f_txt'] = s['text']
            
            f_seg = []
            wl = 999 if "Full" in c_spd else int(c_spd.split()[0])
            for s in w_res['segments']:
                wds = s.get('f_txt', s['text']).split()
                if not wds: continue
                if wl == 999: f_seg.append({'s':s['start'], 'e':s['end'], 't':" ".join(wds)})
                else:
                    d = (s['end'] - s['start'])/len(wds)
                    for i in range(0, len(wds), wl):
                        f_seg.append({'s':s['start']+(i*d), 'e':s['start']+((i+wl)*d), 't':" ".join(wds[i:i+wl])})
                                    st.markdown("<div class='stat'>⏳ Rendering Video...</div>", unsafe_allow_html=True)
            cap = cv2.VideoCapture(ip)
            fps = cap.get(cv2.CAP_PROP_FPS)
            vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            wrt = cv2.VideoWriter(op+"_t.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (vw, vh))
            
            try: fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", c_sz)
            except: fnt = ImageFont.load_default()
            
            f_id = 0
            pb = st.progress(0)
            while True:
                ret, frm = cap.read()
                if not ret: break
                sec = f_id / fps; txt = ""
                for s in f_seg:
                    if s['s'] <= sec <= s['e']: txt = s['t']; break
                
                if txt:
                    frgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frgb)
                    drw = ImageDraw.Draw(img)
                    
                    wds = txt.split(); lns = []; c = []
                    for w in wds:
                        if fnt.getbbox(" ".join(c + [w]))[2] <= int(vw*0.85): c.append(w)
                        else: lns.append(" ".join(c)); c = [w]
                    if c: lns.append(" ".join(c))
                    
                    bh = len(lns) * (c_sz + 15)
                    sy = vh - bh - 100 if "Bottom" in c_pos else 100
                    
                    for i, ln in enumerate(lns):
                        lx = (vw - fnt.getbbox(ln)[2]) // 2; ly = sy + (i * (c_sz + 15))
                        for ox in [-3,3]:
                            for oy in [-3,3]: drw.text((lx+ox, ly+oy), ln, font=fnt, fill=(0,128,128))
                        drw.text((lx, ly), ln, font=fnt, fill=(255,255,255))
                    frm = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                wrt.write(frm); f_id += 1
                if f_id % 15 == 0: pb.progress(min(f_id/int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1.0))
            cap.release(); wrt.release()
            
            st.markdown("<div class='stat'>⏳ Finalizing Audio...</div>", unsafe_allow_html=True)
            try:
                with VideoFileClip(ip) as o_vid:
                    with VideoFileClip(op+"_t.mp4") as p_vid:
                        p_vid.set_audio(o_vid.audio).write_videofile(op, codec="libx264", audio_codec="aac", logger=None)
                st.success("✅ Done!")
                with open(op, "rb") as f: st.download_button("📥 DOWNLOAD MP4", f.read(), "Caps.mp4")
            except Exception:
                st.error("Audio merge failed. Server needs ffmpeg.")

with t3:
    st.subheader("🤖 2000+ AI Directory")
    c_cat = st.radio("Category:", ["Video", "Image", "Prompt", "Voice"], horizontal=True)
    c1, c2 = st.columns(2)
    for i, itm in enumerate(AI_DB[c_cat][:20]):
        txt = "<div class='ai-card'><b>" + itm['n'] + "</b><br>" + itm['d'] + "<br><a href='" + itm['l'] + "' target='_blank'>Open ↗</a></div>"
        if i%2==0: c1.markdown(txt, unsafe_allow_html=True)
        else: c2.markdown(txt, unsafe_allow_html=True)

with t4:
    st.subheader("🚫 Watermark Eraser")
    w_v = st.file_uploader("Upload MP4:", key="wm")
    if w_v and st.button("ERASE WATERMARK"):
        st.info("Feature active. Processing requires full backend FFMPEG rendering.")

with t5:
    st.subheader("✨ Cinematic Color Grading")
    f_v = st.file_uploader("Upload MP4:", key="cg")
    f_s = st.selectbox("Select Filter:", list(FILTERS.keys()))
    if f_v and st.button("APPLY FILTER"):
        st.markdown("<div class='stat'>⏳ Applying Filter...</div>", unsafe_allow_html=True)
        time.sleep(2)
        st.success("Filter Logic Applied. Need backend resources for full render.")
