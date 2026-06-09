import streamlit as st
import time
import requests
import re
from google import genai
from google.genai import types

# 1. पेज का प्रीमियम डिज़ाइन
st.set_page_config(page_title="AI Channel Analyzer", page_icon="📈", layout="centered")

# 2. API Keys Loading
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
    yt_api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception as e:
    st.error("⚠️ Secrets missing! Streamlit me GEMINI_API_KEYS aur YOUTUBE_API_KEY dalo.")
    st.stop()

if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

# 3. 🌌 PURE DARK CINEMATIC CSS
dark_theme_css = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] {
    background-color: #050b14;
    background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #050b14 70%);
    color: #e0e6ed;
}
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
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ==========================================
# 🛠️ HELPER FUNCTION: Fetch YouTube Data
# ==========================================
def get_youtube_data(channel_url, api_key):
    # Extract handle from URL (e.g., @adarshmaurya)
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match:
        return None, "Bhai URL me '@' wala handle nahi mila. Sahi link daal."
    
    handle = handle_match.group(1)
    
    # 1. Get Channel Details
    url1 = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&forHandle={handle}&key={api_key}"
    res1 = requests.get(url1).json()
    
    if "items" not in res1 or len(res1["items"]) == 0:
        return None, "Channel nahi mila. Link check kar."
        
    uploads_playlist_id = res1["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    subs = res1["items"][0]["statistics"].get("subscriberCount", "Hidden")
    
    # 2. Get Latest Videos
    url2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=15&playlistId={uploads_playlist_id}&key={api_key}"
    res2 = requests.get(url2).json()
    
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in res2.get("items", [])]
    if not video_ids:
        return None, "Is channel par koi video nahi hai."
        
    # 3. Get Video Stats (Views, Likes)
    url3 = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
    res3 = requests.get(url3).json()
    
    video_data_list = []
    for item in res3.get("items", []):
        title = item["snippet"]["title"]
        views = item["statistics"].get("viewCount", "0")
        likes = item["statistics"].get("likeCount", "0")
        video_data_list.append(f"Title: '{title}' | Views: {views} | Likes: {likes}")
        
    return {"handle": handle, "subs": subs, "videos": video_data_list}, None

# ==========================================
# FRONT PAGE UI
# ==========================================
st.markdown("<h1 class='glow-title'>AI CHANNEL ANALYZER</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Stop guessing. Let AI decode your algorithm.</p>", unsafe_allow_html=True)
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 🟢 INPUT ZONE
col1, col2 = st.columns(2)
with col1:
    yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
with col2:
    ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername (Optional)")
    
analyze_button = st.button("🚀 Analyze My Digital Identity", use_container_width=True)
st.markdown("---")

# ==========================================
# ANIMATION & AI LOGIC ZONE
# ==========================================
if analyze_button:
    if not yt_link:
        st.warning("⚠️ Bhai, YouTube link toh daal!")
    else:
        status_placeholder = st.empty()
        
        # Loading effect
        status_placeholder.markdown("<div class='matrix-text'>⚡ Initializing connection to YouTube Data API...</div>", unsafe_allow_html=True)
        time.sleep(1)
        
        # 1. Fetch Data
        yt_data, error = get_youtube_data(yt_link, yt_api_key)
        
        if error:
            status_placeholder.empty()
            st.error(error)
        else:
            status_placeholder.markdown("<div class='matrix-text'>⚡ Scraping video metrics & extracting patterns...</div>", unsafe_allow_html=True)
            
            # 2. Prepare AI Prompt
            videos_text = "\n".join(yt_data['videos'])
            
            system_instruction = (
                "You are a ruthless but brilliant AI YouTube & Instagram Strategist. "
                "You favor raw, authentic, and cinematic aesthetics. You integrate poetic weight (wazan) into content strategy. "
                "Analyze the provided YouTube data (titles, views, likes) to find what works best. "
                "Output your analysis EXACTLY in 4 HTML cards using this format:\n\n"
                "<div class='blueprint-card'><h3 style='color: #ff4d4d;'>🚨 1. The Brutal Truth (Diagnosis)</h3><p>[Your brutally honest analysis of their content based on views/titles]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #ffd700;'>🎯 2. The Golden Niche</h3><p>[Your niche recommendation. Recommend raw/authentic themes or self-improvement if data implies it]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #00ffcc;'>⏱️ 3. Timing & Frequency Strategy</h3><p>[Suggest a weekly posting schedule for YT and IG]</p></div>\n"
                "<div class='blueprint-card'><h3 style='color: #ff00ff;'>🚀 4. Your Next 3 Videos (Action Plan)</h3><p>[Provide 3 high-converting video titles/hooks based on their best performing videos]</p></div>\n\n"
                "Do not use markdown code blocks. Just output raw HTML."
            )
            
            user_prompt = f"Here is the data for YouTube Channel @{yt_data['handle']} with {yt_data['subs']} subs.\n\nLatest Videos:\n{videos_text}\n\nTheir Instagram is: {ig_username}. Give me the 4-part Blueprint."
            
# 3. Call Gemini
            chat_success = False
            ai_response = ""
            status_placeholder.markdown("<div class='matrix-text'>⚡ Drafting the 30-Day Masterplan...</div>", unsafe_allow_html=True)
            
            for _ in range(len(api_keys)):
                try:
                    # .strip() lagaya hai taaki extra space automatically hat jaye
                    clean_key = api_keys[st.session_state.current_key_index].strip() 
                    client = genai.Client(api_key=clean_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=user_prompt, 
                        config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
                    )
                    ai_response = response.text
                    chat_success = True
                    break
                except Exception as e:
                    # YE LINE ASLI ERROR DIKHAYEGI
                    st.error(f"⚠️ Asli Error yahan hai: {e}") 
                    st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
            
            status_placeholder.empty()
            
            # 4. Display Output
            if chat_success:
                st.success(f"✅ Deep Analysis Complete for @{yt_data['handle']}!")
                st.markdown(ai_response, unsafe_allow_html=True)
            else:
                st.error("Sab try kar liya, par API nahi chal rahi. Upar wala 'Asli Error' check kar.")
