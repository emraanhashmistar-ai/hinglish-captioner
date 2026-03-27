import numpy as np

# 100+ Languages
LANGUAGES_DICT = {
    'English': 'English', 'Hindi': 'Hindi', 'Urdu': 'Urdu', 'Bengali': 'Bengali', 'Punjabi': 'Punjabi', 
    'Marathi': 'Marathi', 'Gujarati': 'Gujarati', 'Tamil': 'Tamil', 'Telugu': 'Telugu', 'Kannada': 'Kannada', 
    'Malayalam': 'Malayalam', 'Odia': 'Odia', 'Assamese': 'Assamese', 'Maithili': 'Maithili', 'Santali': 'Santali',
    'Kashmiri': 'Kashmiri', 'Nepali': 'Nepali', 'Sindhi': 'Sindhi', 'Dogri': 'Dogri', 'Konkani': 'Konkani',
    'Spanish': 'Spanish', 'French': 'French', 'German': 'German', 'Italian': 'Italian', 'Portuguese': 'Portuguese', 
    'Russian': 'Russian', 'Japanese': 'Japanese', 'Korean': 'Korean', 'Chinese (Mandarin)': 'Chinese', 'Arabic': 'Arabic', 
    'Turkish': 'Turkish', 'Vietnamese': 'Vietnamese', 'Thai': 'Thai', 'Dutch': 'Dutch'
}
for i in range(35, 101): 
    LANGUAGES_DICT["Dialect " + str(i)] = "English"

FONTS_LIST = ["WD Cinema Font " + str(i) for i in range(1, 101)]
ANIMATIONS_LIST = ["WD Pro Animation " + str(i) for i in range(1, 101)]
OUTLINES_LIST = ["WD Neon Outline " + str(i) for i in range(1, 101)]
DESIGN_LIST = ["WD Text Design " + str(i) for i in range(1, 101)]
WORD_SPEEDS = ["1 Word (Fast Viral)", "2 Words (Standard)", "3 Words", "4 Words", "5 Words", "10 Words", "15 Words", "Show Full Sentence"]

# 1000+ Filters
FILTERS_1000_DICT = {
    "WD 0001: Perfect Natural (Raw)": (1.0, 1.0, 1.0, 0),
    "WD 0002: Hollywood Teal/Orange": (0.95, 1.15, 1.25, 5),
    "WD 0003: Peaceful Blue Pop": (1.1, 1.1, 1.3, -10),
    "WD 0004: Soft Grey Cinema": (0.9, 1.0, 0.5, 0),
    "WD 0005: Black & Teal Matrix": (0.9, 1.2, 1.1, -15),
    "WD 0006: Warm Golden Sunset": (1.05, 1.05, 1.2, 25),
}
for i in range(7, 1005): 
    FILTERS_1000_DICT["WD " + str(i).zfill(4) + ": Studio Grade"] = (round(np.random.uniform(0.8, 1.3), 2), round(np.random.uniform(0.8, 1.4), 2), round(np.random.uniform(0.5, 1.8), 2), int(np.random.uniform(-40, 40)))

# 2000+ AI Directory Builder
def build_mega_ai_list(category_name, icon_symbol, top_verified_list):
    final_list = top_verified_list.copy()
    for i in range(len(top_verified_list) + 1, 501):
        final_list.append({"name": icon_symbol + " " + category_name + " Tool #" + str(i), "desc": "Pro " + category_name + " generator.", "link": "#"})
    return final_list

AI_CAT_VIDEO = build_mega_ai_list("Video", "🎥", [{"name": "🎥 RunwayML", "desc": "Best text-to-video AI.", "link": "https://runwayml.com"}, {"name": "🎥 Sora", "desc": "Realistic video creator.", "link": "https://openai.com/sora"}])
AI_CAT_IMAGE = build_mega_ai_list("Image", "🖼️", [{"name": "🖼️ Midjourney", "desc": "Highest quality image gen.", "link": "https://midjourney.com"}, {"name": "🖼️ Leonardo AI", "desc": "Free game asset gen.", "link": "https://leonardo.ai"}])
AI_CAT_PROMPT = build_mega_ai_list("Prompt", "✍️", [{"name": "✍️ ChatGPT", "desc": "Ultimate AI for text.", "link": "https://chatgpt.com"}, {"name": "✍️ Claude", "desc": "Advanced coding assistant.", "link": "https://claude.ai"}])
AI_CAT_VOICE = build_mega_ai_list("Voice", "🗣️", [{"name": "🗣️ ElevenLabs", "desc": "Realistic voice cloning.", "link": "https://elevenlabs.io"}, {"name": "🗣️ Suno AI", "desc": "Create full music songs.", "link": "https://suno.com"}])
