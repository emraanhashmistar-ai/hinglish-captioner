import streamlit as st
import os
import time
import tempfile
import json
import random

st.set_page_config(page_title="WD PRO FF WORLD", layout="wide")

# ---------------- STATE ----------------
if "gender" not in st.session_state:
    st.session_state.gender = None
if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ---------------- UI ----------------
st.markdown("""
<style>
body {background:#000;color:white;}
h1 {
text-align:center;
background:linear-gradient(90deg,#008080,#B4D8E7);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}
.stButton>button {
background:#111;
border:2px solid #008080;
border-radius:10px;
color:white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>WD PRO FF WORLD</h1>", unsafe_allow_html=True)
st.markdown("📺 YouTube: wd_pro_ff | 📸 Instagram: wd_pro_ff")

# ---------------- LOGIN ----------------
if st.session_state.gender is None:
    col1, col2 = st.columns(2)

    if col1.button("👑 I AM KING"):
        st.session_state.gender = "KING"
        st.rerun()

    if col2.button("👸 I AM QUEEN"):
        st.session_state.gender = "QUEEN"
        st.rerun()

    st.stop()

# ---------------- WELCOME ----------------
if not st.session_state.welcome_done:
    st.markdown(f"""
    <h3 style='text-align:center'>
    Every subscriber is my {st.session_state.gender} 👑
    </h3>
    """, unsafe_allow_html=True)

    time.sleep(2)
    st.session_state.welcome_done = True
    st.rerun()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🐼 WD PRO PANDA")

if "scratch" not in st.session_state:
    st.session_state.scratch = False

if not st.session_state.scratch:
    if st.sidebar.button("🎁 GET GIFT"):
        st.sidebar.success("You got 50 coins")
        st.session_state.scratch = True
else:
    st.sidebar.info("Come back tomorrow 😔")

api_key = st.sidebar.text_input("Gemini API", type="password")

# ---------------- TABS ----------------
tabs = st.tabs([
    "⬇️ DOWNLOADER",
    "🎬 CAPTION",
    "🤖 AI",
    "🚫 WATERMARK",
    "✨ COLOR"
])

# ---------------- DOWNLOADER ----------------
with tabs[0]:
    import yt_dlp

    link = st.text_input("Paste Link")
    if st.button("Download"):
        try:
            temp = tempfile.mkdtemp()
            ydl_opts = {
                "outtmpl": f"{temp}/file.%(ext)s",
                "quiet": True,
                "format": "best",
                "extractor_args": {"youtube":{"player_client":["android"]}},
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                path = ydl.prepare_filename(info)

            with open(path, "rb") as f:
                st.download_button("Download File", f)

        except Exception as e:
            st.error(e)

# ---------------- CAPTION ----------------
with tabs[1]:
    video = st.file_uploader("Upload Video", type=["mp4"])

    if st.button("Generate Caption"):
        if video:
            import whisper

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            model = whisper.load_model("base")
            result = model.transcribe(temp.name)
            text = result["text"]

            prompt = f"""
Convert to Hinglish (Roman only).
No Hindi/Urdu script.
Return JSON list.
{text}
"""

            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)

                model_g = genai.GenerativeModel("gemini-1.5-flash")
                res = model_g.generate_content(prompt)

                captions = json.loads(res.text)
                st.write(captions)

            except:
                st.error("Gemini error")

# ---------------- AI DIRECTORY ----------------
with tabs[2]:
    st.header("AI Tools")

    tools = [
        ("ChatGPT","https://chat.openai.com"),
        ("Midjourney","https://midjourney.com"),
        ("RunwayML","https://runwayml.com"),
        ("ElevenLabs","https://elevenlabs.io")
    ]

    for i in range(50):
        tools.append((f"AI Tool {i}","#"))

    for t in tools:
        st.markdown(f"{t[0]} → {t[1]}")

# ---------------- WATERMARK ----------------
with tabs[3]:
    video = st.file_uploader("Upload Video", type=["mp4"])

    x = st.slider("X",0,300,50)
    y = st.slider("Y",0,300,50)
    w = st.slider("W",10,200,100)
    h = st.slider("H",10,200,100)

    if st.button("Remove"):
        if video:
            import cv2

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            cap = cv2.VideoCapture(temp.name)
            out_path = temp.name+"_out.mp4"

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,20,(640,480))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                roi = frame[y:y+h, x:x+w]
                roi = cv2.GaussianBlur(roi,(51,51),0)
                frame[y:y+h, x:x+w] = roi

                out.write(frame)

            cap.release()
            out.release()

            with open(out_path,"rb") as f:
                st.download_button("Download",f)

# ---------------- COLOR GRADING (FIXED) ----------------
with tabs[4]:
    st.header("Color Grading")

    video = st.file_uploader("Upload Video", type=["mp4"])

    brightness = st.slider("Brightness",0.5,2.0,1.0)
    contrast = st.slider("Contrast",0.5,2.0,1.0)
    saturation = st.slider("Saturation",0.5,2.0,1.0)

    if st.button("Apply"):
        if video:
            import cv2
            import numpy as np
            from PIL import Image, ImageEnhance

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            cap = cv2.VideoCapture(temp.name)

            w = int(cap.get(3))
            h = int(cap.get(4))
            fps = int(cap.get(5))

            out_path = temp.name+"_graded.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,fps,(w,h))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                img = Image.fromarray(frame)

                img = ImageEnhance.Brightness(img).enhance(brightness)
                img = ImageEnhance.Contrast(img).enhance(contrast)
                img = ImageEnhance.Color(img).enhance(saturation)

                frame = np.array(img)
                out.write(frame)

            cap.release()
            out.release()

            with open(out_path,"rb") as f:
                st.download_button("Download Video",f)
