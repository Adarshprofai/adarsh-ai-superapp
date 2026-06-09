import streamlit as st
import time
import requests
import re
import os
import tempfile
from google import genai
from google.genai import types

# 1. पेज का प्रीमियम डिज़ाइन
st.set_page_config(page_title="AI Creator Studio", page_icon="📈", layout="centered")

# 2. Session State Initialization
if "analysis_done" not in st.session_state: st.session_state.analysis_done = False
if "yt_data" not in st.session_state: st.session_state.yt_data = None
if "ig_data" not in st.session_state: st.session_state.ig_data = None
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "current_key_index" not in st.session_state: st.session_state.current_key_index = 0

# 3. API Keys Loading
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
    yt_api_key = st.secrets.get("YOUTUBE_API_KEY", "")
    rapid_api_key = st.secrets.get("RAPIDAPI_KEY", "") 
except Exception as e:
    st.error("⚠️ Secrets missing! API Keys check karo.")
    st.stop()

# 4. 🌌 PURE DARK CINEMATIC CSS
dark_theme_css = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] { background-color: #050b14; background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #050b14 70%); color: #e0e6ed; }
.glow-title { text-align: center; font-family: 'Courier New', monospace; font-size: 3rem; font-weight: bold; color: #00ffcc; text-shadow: 0 0 20px rgba(0, 255, 204, 0.4); margin-bottom: 5px; }
.sub-title { text-align: center; color: #8892b0; font-size: 1.1rem; letter-spacing: 1px; margin-top: 0px; margin-bottom: 40px; }
.section-title { color: #ff00ff; font-family: 'Courier New', monospace; font-size: 2rem; margin-top: 40px; margin-bottom: 20px; text-shadow: 0 0 10px rgba(255, 0, 255, 0.4); }
.stTextInput > div > div > input { background-color: rgba(10, 25, 47, 0.6) !important; border: 1px solid #1f4068 !important; color: #00ffcc !important; border-radius: 8px; padding: 12px; font-family: monospace; transition: all 0.3s ease; }
[data-testid="baseButton-secondary"] { background-color: #00ffcc !important; color: #050b14 !important; font-weight: 800 !important; font-size: 1.1rem !important; border-radius: 8px !important; border: none !important; padding: 10px 0px !important; margin-top: 20px !important; transition: all 0.3s ease; }
[data-testid="baseButton-secondary"]:hover { background-color: #00e6b8 !important; transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 204, 0.5) !important; }
.matrix-text { font-family: 'Courier New', Courier, monospace; color: #00ffcc; font-size: 1.2rem; text-align: center; text-shadow: 0 0 8px #00ffcc; margin: 40px 0; }
.blueprint-card { background: rgba(10, 25, 47, 0.7); backdrop-filter: blur(10px); border-left: 4px solid #00ffcc; border: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.blueprint-card h3 { margin-top: 0; font-family: 'Arial', sans-serif; letter-spacing: 0.5px; }
.blueprint-card p, .blueprint-card li { font-size: 1.05rem; line-height: 1.6; color: #ccd6f6; }
.stChatInputContainer { border: 1px solid #00ffcc !important; border-radius: 10px !important; background-color: rgba(10, 25, 47, 0.8) !important; }
textarea { color: #00ffcc !important; -webkit-text-fill-color: #00ffcc !important; }
.stChatMessage { background-color: rgba(10, 25, 47, 0.5) !important; border: 1px solid rgba(0, 255, 204, 0.2); border-radius: 10px; color: white !important; }
[data-testid="stFileUploadDropzone"] { background-color: rgba(10, 25, 47, 0.6) !important; border: 2px dashed #00ffcc !important; }
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================
def get_youtube_data(channel_url, api_key):
    if not api_key: return None, "YouTube API Key missing."
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match: return None, "Bhai URL me '@' wala handle nahi mila."
    handle = handle_match.group(1)
    try:
        url1 = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&forHandle={handle}&key={api_key}"
        res1 = requests.get(url1).json()
        if "items" not in res1 or len(res1["items"]) == 0: return None, "Channel nahi mila."
        uploads_playlist_id = res1["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        subs = res1["items"][0]["statistics"].get("subscriberCount", "Hidden")
        url2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=15&playlistId={uploads_playlist_id}&key={api_key}"
        res2 = requests.get(url2).json()
        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in res2.get("items", [])]
        url3 = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
        res3 = requests.get(url3).json()
        video_data_list = []
        for item in res3.get("items", []):
            title = item["snippet"]["title"]
            views = item["statistics"].get("viewCount", "0")
            video_data_list.append(f"Title: '{title}' | Views: {views}")
        return {"handle": handle, "subs": subs, "videos": video_data_list}, None
    except Exception:
        return None, "YouTube data fetch karne me error aaya."

def get_instagram_data(username, api_key):
    username = username.replace("@", "").strip()
    if not api_key: return {"username": username, "status": "No API Key"}, None
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"}
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data: return {"username": username, "followers": data["data"].get("follower_count", "N/A")}, None
        return {"username": username, "status": "Private profile"}, None
    except Exception: return {"username": username, "status": "API Timeout"}, None

# ==========================================
# FRONT PAGE UI: ZONE 1 (CHANNEL ANALYZER)
# ==========================================
st.markdown("<h1 class='glow-title'>AI CREATOR STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Decode your algorithm. Predict your virality.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 Channel Analyzer", "🎬 Viral Predictor (Video Upload)"])

with tab1:
    col1, col2 = st.columns(2)
    with col1: yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
    with col2: ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername")
        
    analyze_button = st.button("🚀 Analyze Channel Identity", use_container_width=True)
    
    if analyze_button:
        if not yt_link and not ig_username: st.warning("⚠️ Koi ek link toh daal!")
        else:
            status_placeholder = st.empty()
            status_placeholder.markdown("<div class='matrix-text'>⚡ Initializing Data Scraping...</div>", unsafe_allow_html=True)
            
            yt_data, ig_data = None, None
            if yt_link: yt_data, _ = get_youtube_data(yt_link, yt_api_key)
            if ig_username: ig_data, _ = get_instagram_data(ig_username, rapid_api_key)
            
            status_placeholder.markdown("<div class='matrix-text'>⚡ Fusing data for AI analysis...</div>", unsafe_allow_html=True)
            
            user_prompt = "Target Digital Identity:\n"
            if yt_data: user_prompt += f"YouTube: @{yt_data['handle']}.\nLatest Videos:\n{chr(10).join(yt_data['videos'])}\n"
            if ig_data: user_prompt += f"Instagram Info: {ig_data}.\n"
            
            system_instruction = "Output EXACTLY in 4 HTML cards: <div class='blueprint-card'><h3>...</h3><p>...</p></div> for Brutal Truth, Niche, Timing, Next 3 Videos."
            
            chat_success = False
            for _ in range(len(api_keys)):
                try:
                    client = genai.Client(api_key=api_keys[st.session_state.current_key_index].strip())
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=user_prompt, config=types.GenerateContentConfig(system_instruction=system_instruction))
                    st.session_state.ai_response = response.text
                    chat_success = True
                    break
                except Exception:
                    st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
            
            status_placeholder.empty()
            if chat_success:
                st.session_state.yt_data = yt_data
                st.session_state.ig_data = ig_data
                st.session_state.analysis_done = True
                st.success("✅ Analysis Complete!")
                st.markdown(st.session_state.ai_response, unsafe_allow_html=True)

# ==========================================
# FRONT PAGE UI: ZONE 2 (VIRAL PREDICTOR)
# ==========================================
with tab2:
    st.markdown("<h2 class='section-title'>🔮 The Pre-Upload Viral Check</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8892b0;'>Public karne se pehle video yahan daal. AI bata dega chalegi ya pit jayegi.</p>", unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader("📂 Upload Video (MP4/MOV - Keep it under 200MB)", type=["mp4", "mov"])
    predict_button = st.button("👁️ Predict Viral Score & Rank", use_container_width=True)
    
    if predict_button and uploaded_video:
        status_vid = st.empty()
        status_vid.markdown("<div class='matrix-text'>⚡ Uploading video to AI Brain...</div>", unsafe_allow_html=True)
        
        try:
            # Save uploaded video temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_video.read())
                tmp_path = tmp_file.name
            
            client = genai.Client(api_key=api_keys[st.session_state.current_key_index].strip())
            
            # Uploading to Gemini servers
            status_vid.markdown("<div class='matrix-text'>⚡ AI is watching every frame & listening to audio...</div>", unsafe_allow_html=True)
            video_file = client.files.upload(file=tmp_path)
            
            # Wait for processing if needed (Gemini sometimes needs a few secs for videos)
            time.sleep(3) 
            
            # Create Context from Channel Data if it exists
            context = "New User Video."
            if st.session_state.yt_data:
                context = f"This video belongs to YouTube Channel @{st.session_state.yt_data['handle']}. Their past video patterns are: {st.session_state.yt_data['videos']}. Does this new video match their aesthetic and audience?"
            
            video_prompt = f"{context}\nWatch this unreleased video and give me a brutal review before posting. Give output EXACTLY in 4 HTML cards using class='blueprint-card':\n1. <h3 style='color:#ffd700'>🔥 Viral Probability Score (0-100%)</h3><p>[Verdict]</p>\n2. <h3 style='color:#ff4d4d'>🪝 The Hook Check</h3><p>[Rate the first 3 seconds out of 10. Is it engaging?]</p>\n3. <h3 style='color:#00ffcc'>📖 Storyline & Retention</h3><p>[Will they watch till the end? Why or why not?]</p>\n4. <h3 style='color:#ff00ff'>✂️ Editing & Aesthetic</h3><p>[Critique the cuts, audio, text, and raw vibe. What to fix?]</p>\nNo markdown blocks."
            
            status_vid.markdown("<div class='matrix-text'>⚡ Calculating Viral Probability...</div>", unsafe_allow_html=True)
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=[video_file, video_prompt]
            )
            
            # Cleanup temp file
            os.remove(tmp_path)
            
            status_vid.empty()
            st.success("✅ Video Analysis Complete!")
            st.markdown(response.text, unsafe_allow_html=True)
            
        except Exception as e:
            status_vid.empty()
            st.error(f"⚠️ Video upload me error aaya (File too large ya API Limit). Try again. {e}")

st.markdown("---")
