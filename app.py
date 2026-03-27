import streamlit as st
import tempfile
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="WD PRO FF WORLD", layout="wide")

# --------- FILTER ENGINE ---------
def generate_filters():
    filters = []
    for i in range(1000):
        filters.append({
            "name": f"WD {i:04d}",
            "brightness": random.uniform(0.7,1.4),
            "contrast": random.uniform(0.7,1.5),
            "saturation": random.uniform(0.7,1.6),
        })
    return filters

FILTERS = generate_filters()

# --------- LANGUAGE LIST ---------
LANGUAGES = [
    "Hindi","English","Bengali","Tamil","Telugu",
    "Spanish","French","German","Arabic","Urdu"
]

# --------- TEXT DRAW ---------
def draw_text(frame, text, y_pos):
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()

    draw.text((20, y_pos), text, fill=(255,255,255), font=font)
    return np.array(img)
    # --------- UI ---------
st.title("WD PRO FF WORLD")

tab1, tab2, tab3 = st.tabs([
    "🎬 CAPTION PRO",
    "🎨 COLOR PRO",
    "⬇️ DOWNLOADER"
])

# ================= CAPTION =================
with tab1:
    video = st.file_uploader(
        "Upload Video", type=["mp4"], key="cap"
    )

    lang = st.selectbox("Language", LANGUAGES)

    style = st.selectbox("Style", [
        "Word by Word","Full Sentence"
    ])

    if st.button("Generate Subtitle"):
        if video:
            st.info("Processing...")

            import whisper
            model = whisper.load_model("tiny")

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video.read())

            result = model.transcribe(temp.name)
            text = result["text"]

            cap = cv2.VideoCapture(temp.name)

            w = int(cap.get(3))
            h = int(cap.get(4))
            fps = int(cap.get(5))

            out_path = temp.name+"_sub.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,fps,(w,h))

            words = text.split()

            i = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if style == "Word by Word":
                    txt = words[i % len(words)]
                else:
                    txt = text

                frame = draw_text(frame, txt, h-80)

                out.write(frame)
                i += 1

            cap.release()
            out.release()

            with open(out_path,"rb") as f:
                st.download_button("Download Video",f)

# ================= COLOR =================
with tab2:
    video2 = st.file_uploader(
        "Upload Video", type=["mp4"], key="color"
    )

    filter_names = [f["name"] for f in FILTERS]
    choice = st.selectbox("Select Filter", filter_names)

    if st.button("Apply Filter"):
        if video2:
            st.info("Processing...")

            fdata = next(f for f in FILTERS if f["name"] == choice)

            cap = cv2.VideoCapture(
                tempfile.NamedTemporaryFile(
                    delete=False
                ).name
            )

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(video2.read())

            cap = cv2.VideoCapture(temp.name)

            w = int(cap.get(3))
            h = int(cap.get(4))
            fps = int(cap.get(5))

            out_path = temp.name+"_color.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path,fourcc,fps,(w,h))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.convertScaleAbs(
                    frame,
                    alpha=fdata["contrast"],
                    beta=0
                )

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:,:,1] = hsv[:,:,1] * fdata["saturation"]
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

                frame = np.clip(
                    frame * fdata["brightness"],
                    0,255
                ).astype(np.uint8)

                out.write(frame)

            cap.release()
            out.release()

            with open(out_path,"rb") as f:
                st.download_button("Download",f)

# ================= DOWNLOADER =================
with tab3:
    link = st.text_input("Paste Link")

    if st.button("Download"):
        st.warning("Cloud pe YouTube/Instagram block hota hai")
        st.info("Local system pe run karo for real download")
