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
# 1. PAGE CONFIG & MEMORY (Session State)
# ==========================================
st.set_page_config(page_title="AI Creator Studio", page_icon="📈", layout="centered")

# AI की याददाश्त (Memory) के लिए Storage
if "yt_data" not in st.session_state: st.session_state.yt_data = None
if "ig_data" not in st.session_state: st.session_state.ig_data = None
if "video_analysis" not in st.session_state: st.session_state.video_analysis = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "current_key_index" not in st.session_state: st.session_state.current_key_index = 0

# ==========================================
# 2. API KEYS LOADING
# ==========================================
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
    yt_api_key = st.secrets.get("YOUTUBE_API_KEY", "")
    rapid_api_key = st.secrets.get("RAPIDAPI_KEY", "") 
except Exception as e:
    st.error("⚠️ Secrets missing! API Keys check karo.")
    st.stop()

# ==========================================
# 3. PREMIUM DARK & NEON CSS
# ==========================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] { background-color: #050b14; background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #050b14 70%); color: #e0e6ed; }
.section-title { color: #ff00ff; font-family: 'Courier New', monospace; font-size: 1.8rem; margin: 20px 0; text-shadow: 0 0 10px rgba(255, 0, 255, 0.4); }
.stTextInput > div > div > input { background-color: rgba(10, 25, 47, 0.6) !important; border: 1px solid #1f4068 !important; color: #00ffcc !important; border-radius: 8px; padding: 12px; }
[data-testid="baseButton-secondary"] { background-color: #00ffcc !important; color: #050b14 !important; font-weight: 800 !important; border-radius: 8px !important; }
.matrix-text { font-family: 'Courier New', monospace; color: #00ffcc; font-size: 1.1rem; text-align: center; margin: 20px 0; }
.blueprint-card { background: rgba(10, 25, 47, 0.7); border-left: 4px solid #00ffcc; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.final-verdict-card { background: linear-gradient(145deg, rgba(0, 255, 170, 0.1) 0%, rgba(5, 11, 20, 0.9) 100%); border: 2px solid #00ffaa; padding: 25px; border-radius: 12px; }
.stChatInputContainer { border: 1px solid #00ffcc !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

def get_youtube_data(channel_url, api_key):
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match: return None, "Handle missing."
    handle = handle_match.group(1)
    try:
        u1 = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&forHandle={handle}&key={api_key}"
        r1 = requests.get(u1).json()
        up_id = r1["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        subs = r1["items"][0]["statistics"].get("subscriberCount", "N/A")
        u2 = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=10&playlistId={up_id}&key={api_key}"
        r2 = requests.get(u2).json()
        v_ids = [i["snippet"]["resourceId"]["videoId"] for i in r2.get("items", [])]
        u3 = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(v_ids)}&key={api_key}"
        r3 = requests.get(u3).json()
        v_list = [f"Title: {i['snippet']['title']} | Views: {i['statistics'].get('viewCount','0')}" for i in r3.get("items", [])]
        return {"handle": handle, "subs": subs, "videos": v_list}, None
    except: return None, "YT API Error."

# ==========================================
# 5. HEADER & LOGO
# ==========================================
img_b64 = get_base64_image("logo.jpeg")
img_src = f"data:image/jpeg;base64,{img_b64}" if img_b64 else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
    <img src="{img_src}" style="border-radius: 50%; width: 80px; height: 80px; object-fit: cover; border: 3px solid #00ffcc;">
    <div>
        <h1 style="color: #00ffcc; margin: 0; font-size: 2.5rem;">AI CREATOR STUDIO</h1>
        <p style="color: #8892b0; margin: 0;">By Adarsh Maurya • Data-Driven Virality</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 6. MAIN TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📈 Analysis", "🎬 Viral Predictor", "💬 AI Consultant"])

# --- TAB 1: ANALYZER ---
with tab1:
    yt_in = st.text_input("YouTube URL", placeholder="@handle")
    if st.button("🚀 Analyze Channel"):
        with st.spinner("Decoding Channel..."):
            data, err = get_youtube_data(yt_in, yt_api_key)
            if err: st.error(err)
            else:
                st.session_state.yt_data = data
                st.success(f"Channel @{data['handle']} Loaded!")
                st.write(f"Subscribers: {data['subs']}")

# --- TAB 2: PREDICTOR ---
with tab2:
    st.markdown("<h2 class='section-title'>🔮 Video Audit</h2>", unsafe_allow_html=True)
    up_vid = st.file_uploader("Upload MP4", type=["mp4"])
    if st.button("👁️ Predict Success") and up_vid:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(up_vid.read())
            path = tmp.name
        client = genai.Client(api_key=api_keys[st.session_state.current_key_index].strip())
        video_file = client.files.upload(file=path)
        time.sleep(3)
        prompt = "Analyze this video and give Viral Score, Hook Check, and Editing tips in HTML cards."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=[video_file, prompt])
        st.session_state.video_analysis = response.text
        st.markdown(response.text.replace("```html","").replace("```",""), unsafe_allow_html=True)
        os.remove(path)

# --- TAB 3: THE STRATEGIC CHAT (The 3rd Section) ---
with tab3:
    st.markdown("<h2 class='section-title'>💬 AI Strategic Consultant</h2>", unsafe_allow_html=True)
    
    if not st.session_state.yt_data and not st.session_state.video_analysis:
        st.info("Bhai, pehle Channel Analyze kar ya Video upload kar, tabhi AI jawab de payega.")
    else:
        st.markdown("<p style='color:#8892b0;'>AI knows your data. Ask about your strategy, scripts, or fixes.</p>", unsafe_allow_html=True)
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ex: 'Is video ka hook mere channel ke hisab se kaisa hai?'"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            # AI CONTEXT BUILDING
            context = f"""
            You are 'Adarsh Maurya AI'. You have full access to the user's data.
            CHANNEL DATA: {st.session_state.yt_data}
            LAST VIDEO AUDIT: {st.session_state.video_analysis}
            
            Reply in Hinglish (WhatsApp style). Use sarcasm and deep logic. Max 3 lines.
            """
            
            try:
                client = genai.Client(api_key=api_keys[st.session_state.current_key_index].strip())
                res = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[{"role": "user", "parts": [{"text": f"{context}\n\nUser Question: {prompt}"}]}]
                )
                with st.chat_message("assistant"): st.markdown(res.text)
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})
            except:
                st.error("API Limit Over.")
