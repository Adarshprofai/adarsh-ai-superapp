import streamlit as st
import time
import requests
import re
import os
import tempfile
import base64
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE CONFIG & MEMORY STORAGE
# ==========================================
st.set_page_config(page_title="AI Creator Studio Pro", page_icon="📈", layout="centered")

if "current_key_index" not in st.session_state: st.session_state.current_key_index = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_done" not in st.session_state: st.session_state.analysis_done = False
if "yt_data" not in st.session_state: st.session_state.yt_data = None
if "ig_data" not in st.session_state: st.session_state.ig_data = None
if "video_analysis" not in st.session_state: st.session_state.video_analysis = ""
if "ai_response" not in st.session_state: st.session_state.ai_response = ""

# ==========================================
# 2. SECRETS LOADING
# ==========================================
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
    yt_api_key = st.secrets.get("YOUTUBE_API_KEY", "")
    rapid_api_key = st.secrets.get("RAPIDAPI_KEY", "") 
except Exception as e:
    st.error("⚠️ Secrets missing! Streamlit me GEMINI_API_KEYS set karo.")
    st.stop()

# ==========================================
# 3. HIGH-VISIBILITY GLOWING DARK YELLOW CSS
# ==========================================
glowing_yellow_css = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] { 
    background-color: #03070d; 
    background-image: radial-gradient(circle at 50% 0%, #0a111e 0%, #03070d 80%); 
    color: #e2e8f0; 
}
h1, h2, h3, p, span, div, li { color: #ffffff !important; }

/* Section Titles */
.section-title { 
    color: #ffb700 !important; 
    font-family: 'Courier New', monospace; 
    font-size: 2rem; 
    margin-top: 30px; 
    text-shadow: 0 0 15px rgba(255, 183, 0, 0.4); 
}

/* High Visibility Input Boxes */
.stTextInput > div > div > input { 
    background-color: rgba(20, 35, 55, 0.8) !important; 
    border: 2px solid #ffb700 !important; 
    color: #ffffff !important; 
    border-radius: 8px; 
    padding: 12px; 
    font-weight: bold;
    font-family: monospace;
}
.stTextInput > div > div > input:focus {
    box-shadow: 0 0 15px rgba(255, 183, 0, 0.5) !important;
}

/* Glowing Neon Cyan Button for Accents */
[data-testid="baseButton-secondary"] { 
    background-color: #00ffcc !important; 
    color: #03070d !important; 
    font-weight: 800 !important; 
    font-size: 1.1rem !important;
    border-radius: 8px !important; 
    border: none !important;
    padding: 10px 0px !important;
    box-shadow: 0 0 15px rgba(0, 255, 204, 0.3) !important;
}
[data-testid="baseButton-secondary"]:hover {
    background-color: #00e6b8 !important;
    transform: scale(1.01);
    box-shadow: 0 0 25px rgba(0, 255, 204, 0.6) !important;
}

/* Loading Text Matrix Style */
.matrix-text { 
    font-family: 'Courier New', monospace; 
    color: #ffb700; 
    font-size: 1.2rem; 
    text-align: center; 
    text-shadow: 0 0 8px #ffb700; 
    margin: 30px 0; 
}

/* 🔥 CHAMKNE WALE DARK YELLOW CARDS */
.blueprint-card { 
    background: rgba(15, 25, 40, 0.85); 
    backdrop-filter: blur(12px); 
    border: 2px solid #ffb700; 
    padding: 25px; 
    border-radius: 12px; 
    margin-bottom: 25px; 
    box-shadow: 0 0 20px rgba(255, 183, 0, 0.2); 
}
.blueprint-card h3 { margin-top: 0; font-weight: bold; letter-spacing: 0.5px; }
.blueprint-card p, .blueprint-card li { font-size: 1.05rem; line-height: 1.6; color: #e2e8f0 !important; }

/* Ultimate Verdict Glowing Box */
.final-verdict-card { 
    background: linear-gradient(145deg, rgba(255, 183, 0, 0.15) 0%, rgba(3, 7, 13, 0.95) 100%); 
    border: 2.5px solid #ffb700; 
    padding: 30px; 
    border-radius: 12px; 
    margin-top: 35px; 
    box-shadow: 0 0 30px rgba(255, 183, 0, 0.4); 
}
.final-verdict-card h3 { margin-top: 0; color: #ffb700 !important; font-size: 1.6rem; text-transform: uppercase; text-shadow: 0 0 10px rgba(255,183,0,0.3); }
.final-verdict-card p, .final-verdict-card li { font-size: 1.15rem; line-height: 1.7; color: #ffffff !important; }
.final-verdict-card strong { color: #ffcc00 !important; }

/* Chat Container Fixes */
.stChatInputContainer { border: 2px solid #ffb700 !important; border-radius: 10px !important; background-color: rgba(15, 25, 40, 0.9) !important; }
textarea { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
.stChatMessage { background-color: rgba(20, 35, 55, 0.6) !important; border: 1px solid rgba(255, 183, 0, 0.2); border-radius: 10px; }

/* Tabs Design Customization */
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.1rem !important;
    font-weight: bold !important;
}
</style>
"""
st.markdown(glowing_yellow_css, unsafe_allow_html=True)

# ==========================================
# 4. DATA FETCHING BACKEND LOGIC
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

def get_youtube_data(channel_url, api_key):
    if not api_key: return None, "YouTube API Key missing."
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match: return None, "Bhai URL me '@' wala handle sahi se dalo."
    handle = handle_match.group(1)
    try:
        u1 = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&forHandle={handle}&key={api_key}"
        r1 = requests.get(u1).json()
        up_id = r1["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        subs = r1["items"][0]["statistics"].get("subscriberCount", "Hidden")
        u2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=12&playlistId={up_id}&key={api_key}"
        r2 = requests.get(u2).json()
        v_ids = [i["snippet"]["resourceId"]["videoId"] for i in r2.get("items", [])]
        u3 = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(v_ids)}&key={api_key}"
        r3 = requests.get(u3).json()
        v_list = [f"Title: '{i['snippet']['title']}' | Views: {i['statistics'].get('viewCount','0')}" for i in r3.get("items", [])]
        return {"handle": handle, "subs": subs, "videos": v_list}, None
    except: return None, "YouTube server se data nahi nikal paya."

def get_instagram_data(username, api_key):
    username = username.replace("@", "").strip()
    if not api_key: return {"username": username, "status": "No API Key, generic aesthetic analytics active"}, None
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"}
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data: return {"username": username, "followers": data["data"].get("follower_count", "N/A"), "posts": data["data"].get("media_count", "N/A")}, None
        return {"username": username, "status": "Profile fetched"}, None
    except: return {"username": username, "status": "Basic check"}, None

# ==========================================
# 5. BRAND HEADER INTEGRATION
# ==========================================
img_b64 = get_base64_image("logo.jpeg")
img_src = f"data:image/jpeg;base64,{img_b64}" if img_b64 else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

header_html = f"""
<div style="display: flex; align-items: center; justify-content: center; gap: 22px; margin-top: 15px;">
    <img src="{img_src}" style="border-radius: 50%; width: 95px; height: 95px; object-fit: cover; box-shadow: 0 0 25px rgba(255, 183, 0, 0.4); border: 3px solid #ffb700;">
    <div style="display: flex; flex-direction: column;">
        <h1 style="font-family: 'Courier New', monospace; font-size: 2.8rem; font-weight: bold; color: #ffb700; text-shadow: 0 0 20px rgba(255, 183, 0, 0.3); margin: 0; line-height: 1.1;">AI CREATOR STUDIO</h1>
        <p style="color: #8892b0; font-size: 1.1rem; letter-spacing: 1px; margin: 0; padding-top: 6px;">Decode your algorithm. Predict your virality.</p>
    </div>
</div>
<br>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ==========================================
# 6. WORKSPACE TABS (THE CORE 3 SECTIONS)
# ==========================================
tab1, tab2, tab3 = st.tabs(["📈 Channel Analyzer", "🎬 Viral Predictor", "💬 AI Consultant"])

# ----------------- SECTION 1: CHANNEL ANALYZER -----------------
with tab1:
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
    with col2: ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername")
        
    analyze_button = st.button("🚀 Analyze Digital Footprint", use_container_width=True)
    
    if analyze_button:
        if not yt_link and not ig_username: 
            st.warning("⚠️ Bhai, kam se kam YouTube link ya Instagram username me se ek cheez dalo!")
        else:
            status_placeholder = st.empty()
            status_placeholder.markdown("
