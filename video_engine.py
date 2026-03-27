import os
import cv2
import json
import numpy as np
import yt_dlp
import whisper
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
import math

def yt_dlp_download(url, format_type, output_dir):
    # Added anti-bot bypass for streamilt cloud
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    }
    if format_type == 'video':
        ydl_opts['format'] = 'best[ext=mp4]/best'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == 'audio': filename = filename.rsplit('.', 1)[0] + '.mp3'
        return filename

def apply_pil_color_grade(frame_bgr, b_val, c_val, s_val, w_val):
    pil_img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    if b_val != 1.0: pil_img = ImageEnhance.Brightness(pil_img).enhance(b_val)
    if c_val != 1.0: pil_img = ImageEnhance.Contrast(pil_img).enhance(c_val)
    if s_val != 1.0: pil_img = ImageEnhance.Color(pil_img).enhance(s_val)
    image_array = np.array(pil_img).astype(np.int16)
    if w_val != 0:
        r = np.clip(image_array[:,:,0] + w_val, 0, 255)
        b = np.clip(image_array[:,:,2] - w_val, 0, 255)
        image_array = np.stack((r, image_array[:,:,1], b), axis=-1)
    return cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2BGR)

def get_safe_font_engine(size):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception: return ImageFont.load_default()

def advanced_text_wrap(text_string, font_engine, max_allowed_width):
    word_list = text_string.split()
    final_lines = []
    current_line = []
    for word in word_list:
        test_line = " ".join(current_line + [word])
        if font_engine.getbbox(test_line)[2] <= max_allowed_width: current_line.append(word)
        else:
            if current_line: final_lines.append(" ".join(current_line))
            current_line = [word]
    if current_line: final_lines.append(" ".join(current_line))
    return final_lines
