import streamlit as st
import tempfile
import os
import json
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
import whisper
import google.generativeai as genai

st.set_page_config(page_title="Free Hinglish Captioner", page_icon="🎬")

def get_system_font(size):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split(); lines, current = [], []
    for w in words:
        test = " ".join(current + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(" ".join(current)); current = [w]
        else: current.append(w)
    if current: lines.append(" ".join(current))
    return lines

@st.cache_resource
def load_whisper(): return whisper.load_model("base")

def convert_to_hinglish(segments, api_key):
    if not segments: return []
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        input_text = "\n".join([f"{i}|||{s['text']}" for i, s in enumerate(segments)])
        prompt = f"Convert these to natural WhatsApp-style Hinglish. Return ONLY a JSON array of strings. Input:\n{input_text}"
        
        response = model.generate_content(prompt)
        clean_res = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        hinglish_list = json.loads(clean_res)
        
        for i, seg in enumerate(segments):
            seg["hinglish"] = hinglish_list[i] if i < len(hinglish_list) else seg["text"]
    except Exception as e:
        st.warning(f"Gemini error (using original): {e}")
        for seg in segments: seg["hinglish"] = seg["text"]
    return segments

def burn_captions(video_path, segments, output_path, font_size, text_color, position, bg_style):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp_path = output_path.replace(".mp4", "_tmp.mp4")
    writer = cv2.VideoWriter(tmp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    font = get_system_font(font_size)
    r, g, b = int(text_color[1:3], 16), int(text_color[3:5], 16), int(text_color[5:7], 16)
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        curr_time = frame_idx / fps
        active_text = ""
        for s in segments:
            if s['start'] <= curr_time <= s['end']:
                active_text = s.get('hinglish', s['text'])
                break
        
        if active_text:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img)
            lines = wrap_text(draw, active_text, font, int(w*0.8))
            y = h - (len(lines)*font_size) - 60 if position == "Bottom" else 60
            if position == "Center": y = (h - len(lines)*font_size)//2
            for line in lines:
                tw = draw.textbbox((0,0), line, font=font)[2]
                tx = (w - tw)//2
                if bg_style == "Black Bar":
                    draw.rectangle([tx-10, y-5, tx+tw+10, y+font_size+5], fill=(0,0,0,180))
                draw.text((tx, y), line, font=font, fill=(r,g,b))
                y += font_size + 5
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(frame)
        frame_idx += 1
    cap.release(); writer.release()
    
    with VideoFileClip(video_path) as orig:
        with VideoFileClip(tmp_path) as proc:
            final = proc.set_audio(orig.audio) if orig.audio else proc
            final.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

st.title("🎬 Free Hinglish Caption Maker")
with st.sidebar:
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    f_size = st.slider("Size", 16, 72, 32)
    t_color = st.color_picker("Color", "#FFFFFF")
    pos = st.selectbox("Position", ["Bottom", "Center", "Top"])
    bg = st.selectbox("Style", ["Black Bar", "Plain"])

uploaded = st.file_uploader("Upload Video", type=["mp4", "mov"])
if uploaded and api_key:
    if st.button("🚀 Start Process"):
        with tempfile.TemporaryDirectory() as tmpdir:
            v_in, v_out = os.path.join(tmpdir, "in.mp4"), os.path.join(tmpdir, "out.mp4")
            with open(v_in, "wb") as f: f.write(uploaded.getbuffer())
            st.info("🎙️ Transcribing...")
            model = load_whisper()
            res = model.transcribe(v_in)
            st.info("🤖 Converting to Hinglish (Free)...")
            segs = convert_to_hinglish(res['segments'], api_key)
            st.info("🔥 Burning Captions...")
            burn_captions(v_in, segs, v_out, f_size, t_color, pos, bg)
            st.success("✅ Done!")
            st.video(v_out)
            with open(v_out, "rb") as f: st.download_button("📥 Download Video", f, "hinglish_video.mp4")
                
