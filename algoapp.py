import streamlit as st
import time
import requests
import re
from google import genai
from google.genai import types

# 1. पेज का प्रीमियम डिज़ाइन
st.set_page_config(page_title="AI Channel Analyzer", page_icon="📈", layout="centered")

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
    yt_api_key = st.secrets["YOUTUBE_API_KEY"]
    # get() use kiya hai taaki agar key na ho toh app crash na kare
    rapid_api_key = st.secrets.get("RAPIDAPI_KEY", "") 
except Exception as e:
    st.error("⚠️ Secrets missing! GEMINI_API_KEYS aur YOUTUBE_API_KEY dalo.")
    st.stop()

# 4. 🌌 PURE DARK CINEMATIC CSS
dark_theme_css = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] { background-color: #050b14; background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #050b14 70%); color: #e0e6ed; }
.glow-title { text-align: center; font-family: 'Courier New', monospace; font-size: 3rem; font-weight: bold; color: #00ffcc; text-shadow: 0 0 20px rgba(0, 255, 204, 0.4); margin-bottom: 5px; }
.sub-title { text-align: center; color: #8892b0; font-size: 1.1rem; letter-spacing: 1px; margin-top: 0px; margin-bottom: 40px; }
.stTextInput > div > div > input { background-color: rgba(10, 25, 47, 0.6) !important; border: 1px solid #1f4068 !important; color: #00ffcc !important; border-radius: 8px; padding: 12px; font-family: monospace; transition: all 0.3s ease; }
.stTextInput > div > div > input:focus { border: 1px solid #00ffcc !important; box-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important; }
[data-testid="baseButton-secondary"] { background-color: #00ffcc !important; color: #050b14 !important; font-weight: 800 !important; font-size: 1.1rem !important; border-radius: 8px !important; border: none !important; padding: 10px 0px !important; margin-top: 20px !important; transition: all 0.3s ease; }
[data-testid="baseButton-secondary"]:hover { background-color: #00e6b8 !important; transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 204, 0.5) !important; }
.matrix-text { font-family: 'Courier New', Courier, monospace; color: #00ffcc; font-size: 1.2rem; text-align: center; text-shadow: 0 0 8px #00ffcc; margin: 40px 0; }
.blueprint-card { background: rgba(10, 25, 47, 0.7); backdrop-filter: blur(10px); border-left: 4px solid #00ffcc; border: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.blueprint-card h3 { margin-top: 0; font-family: 'Arial', sans-serif; letter-spacing: 0.5px; }
.blueprint-card p, .blueprint-card li { font-size: 1.05rem; line-height: 1.6; color: #ccd6f6; }
.stChatInputContainer { border: 1px solid #00ffcc !important; border-radius: 10px !important; background-color: rgba(10, 25, 47, 0.8) !important; }
textarea { color: #00ffcc !important; -webkit-text-fill-color: #00ffcc !important; }
.stChatMessage { background-color: rgba(10, 25, 47, 0.5) !important; border: 1px solid rgba(0, 255, 204, 0.2); border-radius: 10px; color: white !important; }
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ==========================================
# 🛠️ HELPER FUNCTIONS (YouTube & Instagram APIs)
# ==========================================
def get_youtube_data(channel_url, api_key):
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match: return None, "Bhai URL me '@' wala handle nahi mila. Sahi link daal."
    handle = handle_match.group(1)
    
    url1 = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&forHandle={handle}&key={api_key}"
    res1 = requests.get(url1).json()
    if "items" not in res1 or len(res1["items"]) == 0: return None, "Channel nahi mila."
        
    uploads_playlist_id = res1["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    subs = res1["items"][0]["statistics"].get("subscriberCount", "Hidden")
    
    url2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=15&playlistId={uploads_playlist_id}&key={api_key}"
    res2 = requests.get(url2).json()
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in res2.get("items", [])]
    if not video_ids: return None, "Is channel par koi video nahi hai."
        
    url3 = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
    res3 = requests.get(url3).json()
    
    video_data_list = []
    for item in res3.get("items", []):
        title = item["snippet"]["title"]
        views = item["statistics"].get("viewCount", "0")
        video_data_list.append(f"Title: '{title}' | Views: {views}")
        
    return {"handle": handle, "subs": subs, "videos": video_data_list}, None

def get_instagram_data(username, api_key):
    # Agar RapidAPI key set nahi ki hai, toh error na aaye
    if not api_key:
        return {"username": username, "status": "No API Key, relying on AI assumptions"}, None
        
    username = username.replace("@", "").strip()
    
    # Ye ek standard RapidAPI endpoint ka example hai.
    # (Note: RapidAPI endpoints can change, adjust host if you choose a different specific API)
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                followers = data["data"].get("follower_count", "N/A")
                posts = data["data"].get("media_count", "N/A")
                return {"username": username, "followers": followers, "posts": posts}, None
        return {"username": username, "status": "Private profile ya limit over, checking general aesthetic."}, None
    except Exception as e:
        return {"username": username, "status": f"API Blocked. Basic analysis only."}, None

# ==========================================
# FRONT PAGE UI
# ==========================================
st.markdown("<h1 class='glow-title'>AI CHANNEL ANALYZER</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Stop guessing. Let AI decode your algorithm.</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1: yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
with col2: ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername (Optional)")
    
analyze_button = st.button("🚀 Analyze My Digital Identity", use_container_width=True)
st.markdown("---")

# ==========================================
# BUTTON CLICK LOGIC
# ==========================================
if analyze_button:
    if not yt_link:
        st.warning("⚠️ Bhai, kam se kam YouTube link toh daal!")
    else:
        status_placeholder = st.empty()
        status_placeholder.markdown("<div class='matrix-text'>⚡ Scraping Data cross-platform...</div>", unsafe_allow_html=True)
        
        # Fetching YT
        yt_data, yt_error = get_youtube_data(yt_link, yt_api_key)
        
        # Fetching IG (If provided)
        ig_data = None
        if ig_username:
            ig_data, _ = get_instagram_data(ig_username, rapid_api_key)
        
        if yt_error:
            status_placeholder.empty()
            st.error(yt_error)
        else:
            status_placeholder.markdown("<div class='matrix-text'>⚡ Fusing YouTube metrics with Instagram aesthetic logic...</div>", unsafe_allow_html=True)
            videos_text = "\n".join(yt_data['videos'])
            
            system_instruction = (
                "You are a ruthless but brilliant AI YouTube & Instagram Strategist. "
                "Analyze the provided data to find what works best. "
                "Output your analysis EXACTLY in 4 HTML cards:\n\n"
                "<div class='blueprint-card'><h3 style='color: #ff4d4d;'>🚨 1. The Brutal Truth (Diagnosis)</h3><p>[Analysis based on YT & IG vibe]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #ffd700;'>🎯 2. The Golden Niche</h3><p>[Niche recommendation]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #00ffcc;'>⏱️ 3. Timing & Frequency Strategy</h3><p>[Posting schedule for YT and IG]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #ff00ff;'>🚀 4. Your Next 3 Videos (Action Plan)</h3><p>[3 high-converting hooks for YT/Reels]</p></div>\n\n"
                "Just output raw HTML. No markdown blocks."
            )
            
            user_prompt = f"Data for YT @{yt_data['handle']} ({yt_data['subs']} subs).\nLatest Videos:\n{videos_text}\n"
            if ig_data:
                user_prompt += f"\nInsta Account Info: {ig_data}. Connect their YT topics with Insta Reel logic."
            
            chat_success = False
            response_text = ""
            status_placeholder.markdown("<div class='matrix-text'>⚡ Drafting the 30-Day Masterplan...</div>", unsafe_allow_html=True)
            
            for _ in range(len(api_keys)):
                try:
                    clean_key = api_keys[st.session_state.current_key_index].strip()
                    client = genai.Client(api_key=clean_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=user_prompt, 
                        config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
                    )
                    response_text = response.text
                    chat_success = True
                    break
                except Exception:
                    st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
            
            status_placeholder.empty()
            
            if chat_success:
                st.session_state.yt_data = yt_data
                st.session_state.ig_data = ig_data
                st.session_state.ai_response = response_text
                st.session_state.analysis_done = True
                st.session_state.chat_history = []
            else:
                st.error("⚠️ API Down! Bhai thodi der me try kar.")

# ==========================================
# DISPLAY ZONE & CHAT INTERFACE
# ==========================================
if st.session_state.analysis_done:
    st.success(f"✅ Analysis Complete for @{st.session_state.yt_data['handle']}!")
    st.markdown(st.session_state.ai_response, unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h2 class='glow-title' style='font-size: 2rem; color: #ff00ff;'>💬 Cross-Examine The AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8892b0;'>Pucho kuch bhi. Niche wala hook pasand nahi aaya? Naya maang lo.</p>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

    user_chat = st.chat_input("Apne doubts yaha type kar bhai...")

    if user_chat:
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_chat)
        st.session_state.chat_history.append({"role": "user", "content": user_chat})
        
        chat_instruction = (
            "तुम्हारा नाम 'Adarsh Maurya AI' है। एकदम WhatsApp वाले short forms (thk, kya, bhi, yrr) use karo. Emoji bilkul mat lagao. "
            "Sarcasm aur jokes ka use karo. "
            f"TUNE ABHI IS CHANNEL KO ANALYZE KIYA HAI: {st.session_state.yt_data}. "
            f"INSTA DATA: {st.session_state.ig_data}. "
            f"TERA DIYA GAYA ROADMAP YE HAI: {st.session_state.ai_response}. "
            "User ab tujhse is roadmap par sawaal puch raha hai. Use brutally honest aur clear reply de. Maximum 2-3 lines."
        )
        
        gemini_history = []
        for m in st.session_state.chat_history:
            r = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": r, "parts": [m["content"]]})
            
        chat_success = False
        for _ in range(len(api_keys)):
            try:
                clean_key = api_keys[st.session_state.current_key_index].strip()
                client = genai.Client(api_key=clean_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=gemini_history, 
                    config=types.GenerateContentConfig(system_instruction=chat_instruction, temperature=0.7)
                )
                with st.chat_message("assistant", avatar="🤖"): st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                chat_success = True
                break
            except Exception as e:
                st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
                
        if not chat_success: st.error("⚠️ AI ka dimag hang ho gaya (Limit over).")
