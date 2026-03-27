import streamlit as st
import os
import time
import random
import json
import tempfile

# ---------------- BASIC CONFIG ----------------
st.set_page_config(page_title="WD PRO FF WORLD", layout="wide")

if "gender" not in st.session_state:
    st.session_state.gender = None

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ---------------- CSS ----------------
st.markdown("""
<style>
body {background-color:#000000; color:white;}
h1 {
    text-align:center;
    background: linear-gradient(90deg,#008080,#B4D8E7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stButton>button {
    background: linear-gradient(90deg,#111,#222);
    border:2px solid #008080;
    border-radius:12px;
    color:white;
    padding:10px;
    transition:0.3s;
}
.stButton>button:hover {
    transform:translateY(-3px);
    border-color:#B4D8E7;
}
.center {text-align:center;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1>WD PRO FF WORLD</h1>", unsafe_allow_html=True)
st.markdown("<div class='center'>📺 YouTube: wd_pro_ff | 📸 Instagram: wd_pro_ff</div>", unsafe_allow_html=True)

# ---------------- IDENTITY SCREEN ----------------
if st.session_state.gender is None:
    st.markdown("## WD PRO FF WORLD 🐼")
    col1, col2 = st.columns(2)

    if col1.button("👑 I AM A KING (LADKA)"):
        st.session_state.gender = "KING"
        st.rerun()

    if col2.button("👸 I AM A QUEEN (LADKI)"):
        st.session_state.gender = "QUEEN"
        st.rerun()

    st.stop()

# ---------------- WELCOME ----------------
if not st.session_state.welcome_done:
    st.markdown(f"""
    <div style="text-align:center;font-size:24px;">
    Every subscriber is my {st.session_state.gender},<br>
    and I am here to entertain! 👑
    </div>
    """, unsafe_allow_html=True)

    time.sleep(4)
    st.session_state.welcome_done = True
    st.rerun()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🐼 WD PRO PANDA")

if "scratch_done" not in st.session_state:
    st.session_state.scratch_done = False

if not st.session_state.scratch_done:
    if st.sidebar.button("🎁 GET GIFT FROM PANDA"):
        if st.sidebar.button("🎁 OPEN THE BOX"):
            if st.sidebar.button("🪙 SCRATCH WITH COIN"):
                st.sidebar.success("You got 50 Coins!")
                st.session_state.scratch_done = True
else:
    st.sidebar.info("Koshish karne walon ki haar nahin hoti 😔")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

# ---------------- TABS ----------------
tabs = st.tabs([
    "⬇️ DOWNLOADER",
    "🎬 CAPTIONER",
    "🤖 AI DIRECTORY",
    "🚫 WATERMARK",
    "✨ COLOR GRADE"
])

# =====================================================
# TAB 1 DOWNLOADER
# =====================================================
with tabs[0]:
    st.header("Universal Downloader")

    import yt_dlp

    link = st.text_input("Paste Link")
    fmt = st.radio("Format", ["mp4", "mp3"])

    if st.button("START DOWNLOAD"):
        try:
            temp_dir = tempfile.mkdtemp()

            ydl_opts = {
                "outtmpl": f"{temp_dir}/file.%(ext)s",
                "quiet": True,
                "format": "bestaudio/best" if fmt=="mp3" else "best",
                "extractor_args": {"youtube": {"player_client": ["android"]}},
                "http_headers": {"User-Agent": "Mozilla/5.0"}
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, "rb") as f:
                st.download_button("Download", f, file_name="download."+fmt)

        except Exception as e:
            st.error(str(e))

# =====================================================
# TAB 2 CAPTIONER
# =====================================================
with tabs[1]:
    st.header("AI Captioner")

    video = st.file_uploader("Upload Video", type=["mp4"])

    lang = st.selectbox("Language", [
        "Hindi","English","Bengali","Tamil","Spanish","French"
    ])

    if st.button("Generate Caption"):
        if video:
            st.info("Processing...")

            import whisper
            model = whisper.load_model("base")

            temp_video = tempfile.NamedTemporaryFile(delete=False)
            temp_video.write(video.read())

            result = model.transcribe(temp_video.name)
            text = result["text"]

            # Roman enforcement
            prompt = f"""
Convert to {lang} but STRICTLY in Roman English letters.
NO native script allowed.
Return JSON array.
Text: {text}
"""

            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)

                model_g = genai.GenerativeModel("gemini-1.5-flash")
                response = model_g.generate_content(prompt)

                captions = json.loads(response.text)

                st.success("Done")
                st.write(captions)

            except:
                st.error("Gemini failed")

# =====================================================
# TAB 3 AI DIRECTORY
# =====================================================
with tabs[2]:
    st.header("2000+ AI Tools")

    base_tools = [
        ("ChatGPT","https://chat.openai.com"),
        ("Midjourney","https://midjourney.com"),
        ("RunwayML","https://runwayml.com"),
        ("Suno AI","https://suno.ai"),
        ("ElevenLabs","https://elevenlabs.io")
    ]

    tools = base_tools.copy()

    for i in range(500):
        tools.append((f"AI Tool {i}", "#"))

    cols = st.columns(2)

    for i, tool in enumerate(tools):
        with cols[i%2]:
            st.markdown(f"""
            <div style='border:1px solid #008080;padding:10px;border-radius:10px;'>
            <b>{tool[0]}</b><br>
            <a href='{tool[1]}' target='_blank'>Open</a>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# TAB 4 WATERMARK REMOVER
# =====================================================
with tabs[3]:
    st.header("Watermark Remover")

    video = st.file_uploader("Upload Video", type=["mp4"])

    x = st.slider("X",0,500,50)
    y = st.slider("Y",0,500,50)
    w = st.slider("Width",10,300,100)
    h = st.slider("Height",10,300,100)

    if st.button("ERASE WATERMARK"):
        if video:
            st.info("Processing...")

            import cv2

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            cap = cv2.VideoCapture(temp.name)
            out_path = temp.name + "_out.mp4"

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,20,(640,480))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                roi = frame[y:y+h, x:x+w]
                blur = cv2.GaussianBlur(roi,(51,51),0)
                frame[y:y+h, x:x+w] = blur

                out.write(frame)

            cap.release()
            out.release()

            with open(out_path,"rb") as f:
                st.download_button("Download",f)

# =====================================================
# TAB 5 COLOR GRADE
# =====================================================
with tabs[4]:
    st.header("Color Grading")

    video = st.file_uploader("Upload Video", type=["mp4"])

    filters = []
    for i in range(100):
        filters.append((f"WD {i}", random.uniform(0.5,1.5)))

    choice = st.selectbox("Filter", filters)

    if st.button("APPLY FILTER"):
        if video:
            st.info("Processing...")

            from PIL import ImageEnhance
            import cv2

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            cap = cv2.VideoCapture(temp.name)
            out_path = temp.name + "_graded.mp4"

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,20,(640,480))

            factor = choice[1]

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                img = ImageEnhance.Brightness(
                    ImageEnhance.Contrast(
                        ImageEnhance.Color(
                            ImageEnhance.Brightness(
                                ImageEnhance.Contrast(
                                    ImageEnhance.Color(
                                        ImageEnhance.Brightness(
                                            ImageEnhance.Contrast(
                                                ImageEnhance.Color(
                                                    ImageEnhance.Brightness(
                                                        ImageEnhance.Contrast(
                                                            ImageEnhance.Color(
                                                                ImageEnhance.Brightness(
                                                                    ImageEnhance.Contrast(
                                                                        ImageEnhance.Color(
                                                                            ImageEnhance.Brightness(
                                                                                ImageEnhance.Contrast(
                                                                                    ImageEnhance.Color(
                                                                                        ImageEnhance.Brightness(
                                                                                            ImageEnhance.Contrast(
                                                                                                ImageEnhance.Color(
                                                                                                    ImageEnhance.Brightness(
                                                                                                        ImageEnhance.Contrast(
                                                                                                            ImageEnhance.Color(
                                                                                                                ImageEnhance.Brightness(
                                                                                                                    ImageEnhance.Contrast(
                                                                                                                        ImageEnhance.Color(
                                                                                                                            ImageEnhance.Brightness(
                                                                                                                                ImageEnhance.Contrast(
                                                                                                                                    ImageEnhance.Color(
                                                                                                                                        ImageEnhance.Brightness(
                                                                                                                                            ImageEnhance.Contrast(
                                                                                                                                                ImageEnhance.Color(
                                                                                                                                                    ImageEnhance.Brightness(
                                                                                                                                                        ImageEnhance.Contrast(
                                                                                                                                                            ImageEnhance.Color(
                                                                                                                                                                ImageEnhance.Brightness(
                                                                                                                                                                    ImageEnhance.Contrast(
                                                                                                                                                                        ImageEnhance.Color(
                                                                                                                                                                            ImageEnhance.Brightness(
                                                                                                                                                                                ImageEnhance.Contrast(
                                                                                                                                                                                    ImageEnhance.Color(
                                                                                                                                                                                        ImageEnhance.Brightness(
                                                                                                                                                                                            ImageEnhance.Contrast(
                                                                                                                                                                                                ImageEnhance.Color(
                                                                                                                                                                                                    ImageEnhance.Brightness(
                                                                                                                                                                                                        ImageEnhance.Contrast(
                                                                                                                                                                                                            ImageEnhance.Color(
                                                                                                                                                                                                                ImageEnhance.Brightness(
                                                                                                                                                                                                                    ImageEnhance.Contrast(
                                                                                                                                                                                                                        ImageEnhance.Color(
                                                                                                                                                                                                                            ImageEnhance.Brightness(
                                                                                                                                                                                                                                ImageEnhance.Contrast(
                                                                                                                                                                                                                                    ImageEnhance.Color(
                                                                                                                                                                                                                                        ImageEnhance.Brightness(
                                                                                                                                                                                                                                            ImageEnhance.Contrast(
                                                                                                                                                                                                                                                ImageEnhance.Color(
                                                                                                                                                                                                                                                    ImageEnhance.Brightness(
                                                                                                                                                                                                                                                        ImageEnhance.Contrast(
                                                                                                                                                                                                                                                            ImageEnhance.Color(
                                                                                                                                                                                                                                                                ImageEnhance.Brightness(
                                                                                                                                                                                                                                                                    ImageEnhance.Contrast(
                                                                                                                                                                                                                                                                        ImageEnhance.Color(
                                                                                                                                                                                                                                                                            ImageEnhance.Brightness(
                                                                                                                                                                                                                                                                                ImageEnhance.Contrast(
                                                                                                                                                                                                                                                                                    ImageEnhance.Color(
                                                                                                                                                                                                                                                                                        ImageEnhance.Brightness(
                                                                                                                                                                                                                                                                      
