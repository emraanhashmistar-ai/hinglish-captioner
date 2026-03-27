import streamlit as st
import tempfile
import time
import json

st.set_page_config(page_title="WD PRO FF WORLD", layout="wide")

# ---------- STATE ----------
if "gender" not in st.session_state:
    st.session_state.gender = None
if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ---------- UI ----------
st.markdown("""
<style>
body {background:#000;color:white;}
h1 {
text-align:center;
background:linear-gradient(90deg,#008080,#B4D8E7);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>WD PRO FF WORLD</h1>", unsafe_allow_html=True)
st.write("📺 YouTube: wd_pro_ff | 📸 Instagram: wd_pro_ff")

# ---------- LOGIN ----------
if st.session_state.gender is None:
    col1, col2 = st.columns(2)

    if col1.button("👑 I AM KING"):
        st.session_state.gender = "KING"
        st.rerun()

    if col2.button("👸 I AM QUEEN"):
        st.session_state.gender = "QUEEN"
        st.rerun()

    st.stop()

# ---------- WELCOME ----------
if not st.session_state.welcome_done:
    st.markdown(f"### Welcome {st.session_state.gender} 👑")
    time.sleep(2)
    st.session_state.welcome_done = True
    st.rerun()

# ---------- SIDEBAR ----------
st.sidebar.title("🐼 WD PRO PANDA")
api_key = st.sidebar.text_input("Gemini API", type="password")

# ---------- TABS ----------
tabs = st.tabs([
    "⬇️ DOWNLOADER",
    "🎬 CAPTION",
    "🚫 WATERMARK",
    "✨ COLOR"
])# ================= DOWNLOADER =================
with tabs[0]:
    link = st.text_input("Paste Link")

    if st.button("Download"):
        st.warning("Streamlit cloud pe downloader block hota hai.")
        st.info("Local system pe run karo for full working.")

# ================= CAPTION =================
with tabs[1]:
    video1 = st.file_uploader(
        "Upload Video", type=["mp4"], key="cap"
    )

    if st.button("Generate Caption"):
        if video1:
            st.info("Processing...")

            try:
                import whisper

                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(video1.read())

                model = whisper.load_model("tiny")
                result = model.transcribe(temp.name)

                st.success("Done")
                st.text(result["text"])

            except Exception as e:
                st.error(str(e))

# ================= WATERMARK =================
with tabs[2]:
    video2 = st.file_uploader(
        "Upload Video", type=["mp4"], key="wm"
    )

    if st.button("Remove Watermark"):
        if video2:
            st.warning("Heavy processing cloud pe fail ho sakta hai.")
            st.info("Local pe run karo for best result.")

# ================= COLOR =================
with tabs[3]:
    video3 = st.file_uploader(
        "Upload Video", type=["mp4"], key="color"
    )

    brightness = st.slider("Brightness",0.5,2.0,1.0)
    contrast = st.slider("Contrast",0.5,2.0,1.0)

    if st.button("Apply Color"):
        if video3:
            st.warning("Video processing cloud pe unstable hai.")
