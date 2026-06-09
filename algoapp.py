import streamlit as st
import time
import requests
import re
import os
import tempfile
from google import genai
from google.genai import types

# 1. Page Config
st.set_page_config(page_title="Adarsh Maurya AI - Premium", page_icon="🧑‍💻", layout="wide")

# 2. Session State Initialization
if "current_key_index" not in st.session_state: st.session_state.current_key_index = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_done" not in st.session_state: st.session_state.analysis_done = False
if "yt_data" not in st.session_state: st.session_state.yt_data = None
if "ig_data" not in st.session_state: st.session_state.ig_data = None
if "ai_response" not in st.session_state: st.session_state.ai_response = ""

# 3. API Keys Loading
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
    # Non-blocking get for others while testing
    yt_api_key = st.secrets.get("YOUTUBE_API_KEY", "")
    rapid_api_key = st.secrets.get("RAPIDAPI_KEY", "") 
except Exception as e:
    st.error("⚠️ Secrets missing! streamlt settings -> secrets me GEMINI_API_KEYS dalo.")
    st.stop()

# 4. Pure Dark Cinematic & Neon CSS
dark_theme_css = """
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
[data-testid="stAppViewContainer"] { background-color: #050b14; background-image: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #050b14 70%); color: #e0e6ed; }
h1, h2, h3, p, span, div { color: #ffffff !important; }

/* Main Title Flexbox Alignment for Logo */
.brand-header-container { 
    display: flex; align-items: center; justify-content: start; gap: 25px; margin-top: 50px; 
}

.brand-text-stack {
    display: flex; flex-direction: column; align-items: start;
}

.glow-title { 
    font-family: 'Courier New', monospace; font-size: 3rem; font-weight: bold; 
    color: #00ffcc; text-shadow: 0 0 20px rgba(0, 255, 204, 0.4); margin: 0;
}
.sub-title { color: #8892b0; font-size: 1.1rem; letter-spacing: 1px; margin: 0; padding-top: 5px;}

/* Section Titles */
.section-title { color: #ff00ff; font-family: 'Courier New', monospace; font-size: 2rem; margin-top: 40px; margin-bottom: 20px; text-shadow: 0 0 10px rgba(255, 0, 255, 0.4); }

/* Sleek Inputs */
.stTextInput > div > div > input { background-color: rgba(10, 25, 47, 0.6) !important; border: 1px solid #1f4068 !important; color: #00ffcc !important; border-radius: 8px; padding: 12px; font-family: monospace; transition: all 0.3s ease; }
.stTextInput > div > div > input:focus { border: 1px solid #00ffcc !important; box-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important; }

/* Main Button */
[data-testid="baseButton-secondary"] { background-color: #00ffcc !important; color: #050b14 !important; font-weight: 800 !important; font-size: 1.1rem !important; border-radius: 8px !important; border: none !important; padding: 10px 0px !important; margin-top: 20px !important; transition: all 0.3s ease; }
[data-testid="baseButton-secondary"]:hover { background-color: #00e6b8 !important; transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 204, 0.5) !important; }

/* Hacker Loading Text Matrix Style */
.matrix-text { font-family: 'Courier New', Courier, monospace; color: #00ffcc; font-size: 1.2rem; text-align: center; text-shadow: 0 0 8px #00ffcc; margin: 40px 0; }

/* Glassmorphism Output Cards */
.blueprint-card { background: rgba(10, 25, 47, 0.7); backdrop-filter: blur(10px); border-left: 4px solid #00ffcc; border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.blueprint-card h3 { margin-top: 0; font-family: 'Arial', sans-serif; letter-spacing: 0.5px; }
.blueprint-card p, .blueprint-card li { font-size: 1.05rem; line-height: 1.6; color: #ccd6f6; }

/* Final Verdict Neon Box */
.final-verdict-card { background: linear-gradient(145deg, rgba(0, 255, 170, 0.1) 0%, rgba(5, 11, 20, 0.9) 100%); border: 2px solid #00ffaa; padding: 30px; border-radius: 12px; margin-top: 40px; margin-bottom: 25px; box-shadow: 0 0 25px rgba(0, 255, 170, 0.3); }
.final-verdict-card h3 { margin-top: 0; color: #00ffaa; font-family: 'Arial', sans-serif; font-size: 1.5rem; text-transform: uppercase;}
.final-verdict-card p, .final-verdict-card li { font-size: 1.15rem; line-height: 1.7; color: #ffffff; }
.final-verdict-card strong { color: #ffd700; }

/* Dropzone Styling */
[data-testid="stFileUploadDropzone"] { background-color: rgba(10, 25, 47, 0.6) !important; border: 2px dashed #00ffcc !important; }

/* Chat Styling */
.stChatInputContainer { border: 1px solid #00ffcc !important; border-radius: 10px !important; background-color: rgba(10, 25, 47, 0.8) !important; }
textarea { color: #00ffcc !important; -webkit-text-fill-color: #00ffcc !important; }
.stChatMessage { background-color: rgba(10, 25, 47, 0.5) !important; border: 1px solid rgba(0, 255, 204, 0.2); border-radius: 10px; color: white !important; }
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ==========================================
# 5. Helper Functions
# ==========================================
def get_youtube_data(channel_url, api_key):
    if not api_key: return None, "YouTube API Key missing."
    handle_match = re.search(r'@([a-zA-Z0-9_-]+)', channel_url)
    if not handle_match: return None, "Bhai URL me '@' wala handle nahi mila. Sahi link daal."
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
    except Exception: return None, "YouTube data fetch me error aaya."

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
# 6. Main UI Block
# ==========================================

# 🔥🟢 FLEXBOX CONTAINING LOGO & TEXT FOR THE HEADER
main_title_html = """
<div class='brand-header-container'>
    <img src='[YOUR_IMAGE_URL_HERE]' style='border-radius: 50%; width: 80px; height: 80px; object-fit: cover; box-shadow: 0 0 20px rgba(0, 255, 204, 0.4); border: 2px solid rgba(0, 255, 204, 0.3);'>
    
    <div class='brand-text-stack'>
        <h1 class='glow-title'>Adarsh Maurya AI</h1>
        <p class='sub-title'>Raw Intelligence. Unfiltered Vibe.</p>
    </div>
</div>
"""
st.markdown(main_title_html, unsafe_allow_html=True)
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Channel Analyzer", "🎬 Viral Predictor", "🗑️ The Mental Flush"])

# ----------------- TAB 1: CHANNEL ANALYZER -----------------
with tab1:
    col1, col2 = st.columns(2)
    with col1: yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
    with col2: ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername")
        
    analyze_button = st.button("🚀 Analyze Channel Identity", use_container_width=True)
    
    if analyze_button:
        if not yt_link and not ig_username: st.warning("⚠️ Koi ek link toh daal!")
        else:
            status_placeholder = st.empty()
            status_placeholder.markdown("<div class='matrix-text'>⚡ Fetching data...</div>", unsafe_allow_html=True)
            
            yt_data, ig_data = None, None
            if yt_link: yt_data, _ = get_youtube_data(yt_link, yt_api_key)
            if ig_username: ig_data, _ = get_instagram_data(ig_username, rapid_api_key)
            
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
                st.session_state.analysis_done = True
                st.success("✅ Analysis Complete!")
                st.markdown(st.session_state.ai_response, unsafe_allow_html=True)

# ----------------- TAB 2: VIRAL PREDICTOR -----------------
with tab2:
    st.markdown("<h2 class='section-title'>🔮 Pre-Upload Viral Prediction</h2>", unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader("📂 Upload Video (MP4/MOV < 200MB)", type=["mp4", "mov"])
    predict_button = st.button("👁️ Predict Viral Score & Rank", use_container_width=True)
    
    if predict_button and uploaded_video:
        status_vid = st.empty()
        status_vid.markdown("<div class='matrix-text'>⚡ Uploading video to AI Brain...</div>", unsafe_allow_html=True)
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_video.read())
                tmp_path = tmp_file.name
            
            client = genai.Client(api_key=api_keys[st.session_state.current_key_index].strip())
            
            status_vid.markdown("<div class='matrix-text'>⚡ AI is watching every frame...</div>", unsafe_allow_html=True)
            video_file = client.files.upload(file=tmp_path)
            time.sleep(3) 
            
            context = "New User Video."
            if st.session_state.yt_data:
                context = f"Video belongs to YouTube @{st.session_state.yt_data['handle']}. Their past video patterns: {st.session_state.yt_data['videos']}."
            
            video_prompt = f"{context}\nWatch this unreleased video and give a brutal review. Outputraw HTML with class='blueprint-card' for Viral Score (0-100%), Hook Check (out of 10), Storyline & Retention, Editing & Aesthetic. Then, EXACTLY ONE class='final-verdict-card' at the bottom. The first card should be <h3 style='color:#ffd700'>🔥 Viral Probability Score</h3>, second <h3 style='color:#ff4d4d'>🪝 The Hook Check</h3>, third <h3 style='color:#00ffcc'>📖 Storyline & Retention</h3>, fourth <h3 style='color:#ff00ff'>✂️ Editing & Aesthetic</h3>, and final verdict card <h3 style='color:#00ffaa'>💡 Final Verdict & Steps</h3>."
            
            status_vid.markdown("<div class='matrix-text'>⚡ Calculating Probability...</div>", unsafe_allow_html=True)
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=[video_file, video_prompt])
            
            os.remove(tmp_path)
            status_vid.empty()
            st.success("✅ Analysis Complete!")
            st.markdown(response.text, unsafe_allow_html=True)
            
        except Exception as e:
            status_vid.empty()
            st.error(f"⚠️ Video error. {e}")

# ----------------- TAB 3: THE MENTAL FLUSH -----------------
with tab3:
    st.markdown("<h1 style='text-align: center; color: white;'>🗑️ THE MENTAL FLUSH</h1>", unsafe_allow_html=True)
    # Original Mental Flush integration
    flush_html = """
    <!DOCTYPE html><html><head><style>
        body { text-align: center; background: transparent; overflow: hidden; font-family: sans-serif; color: white; margin: 0;}
        .bin-container { position: relative; width: 100%; height: 260px; overflow: hidden; background: rgba(10,10,10,0.4); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-top: 20px;}
        .dustbin { width: 90px; height: 110px; border: 3px solid #666; border-top: none; position: absolute; bottom: 40px; left: calc(50% - 45px); border-radius: 0 0 15px 15px; background: rgba(0,0,0,0.8); z-index: 10; cursor: pointer; transition: 0.3s; box-shadow: inset 0 -15px 20px rgba(0,0,0,0.8); }
        .dustbin:hover { box-shadow: 0 0 15px rgba(255,0,0,0.3); border-color: #888;}
        .lid { width: 100px; height: 10px; background: #555; position: absolute; top: -10px; left: -5px; border-radius: 5px; transform-origin: left; transition: transform 0.4s ease-in-out; }
        .dustbin.open .lid { transform: rotate(-70deg); background: #777;}
        .mic { position: absolute; font-size: 30px; top: 20px; left: 30px; opacity: 0; transition: 0.5s; z-index: 5; }
        .dustbin.open .mic { top: -45px; opacity: 1; animation: pulse 1s infinite alternate; }
        @keyframes pulse { 0% { transform: scale(1); text-shadow: 0 0 10px red;} 100% { transform: scale(1.1); text-shadow: 0 0 20px red;} }
        .word { position: absolute; font-size: 16px; font-weight: bold; color: #ff3333; opacity: 0; z-index: 2; text-shadow: 0 0 5px red; white-space: nowrap;}
        #flushBtn { display: none; position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); padding: 5px 15px; background: #aa0000; color: white; border: 1px solid #ff0000; border-radius: 5px; font-size: 14px; cursor: pointer; font-weight: bold;}
        #flushBtn:hover { background: #ff0000; box-shadow: 0 0 15px rgba(255,0,0,0.8); }
        #statusText { font-size: 12px; color: #bbb; margin-top: 10px;}
    </style></head><body>
    <div class="bin-container" id="container"><p id="statusText">Tap bin & speak stress out</p>
    <div class="dustbin" id="bin" onclick="toggleBin()"><div class="lid"></div><div class="mic">🎙️</div></div>
    <button id="flushBtn" onclick="flushIt()">FLUSH IT</button></div>
    <audio id="boomSound" src="https://assets.mixkit.co/active_storage/sfx/119/119-preview.mp3"></audio>
    <audio id="flushSound" src="https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"></audio>
    <script>
        let bin = document.getElementById('bin'); let statusText = document.getElementById('statusText'); let flushBtn = document.getElementById('flushBtn'); let isOpen = false; let recognition; let wordsDropped = 0;
        if ('webkitSpeechRecognition' in window) { recognition = new webkitSpeechRecognition(); recognition.continuous = true; recognition.interimResults = false; recognition.lang = 'hi-IN'; recognition.onresult = function(event) { for (let i = event.resultIndex; i < event.results.length; ++i) { if (event.results[i].isFinal) { let text = event.results[i][0].transcript.trim(); let words = text.split(' '); words.forEach((w, index) => { setTimeout(() => dropWord(w), index * 300); }); wordsDropped += words.length; if(wordsDropped > 0 && isOpen) { setTimeout(() => { flushBtn.style.display = "block"; }, 1500); } } } }; }
        function toggleBin() { if(!isOpen) { bin.classList.add('open'); statusText.innerText = "Listening..."; isOpen = true; if(recognition) recognition.start(); } else { bin.classList.remove('open'); statusText.innerText = "Locked. Flush?"; isOpen = false; if(recognition) recognition.stop(); } }
        function dropWord(text) { let w = document.createElement('div'); w.className = 'word'; w.innerText = text; let startX = 20 + Math.random() * 150; w.style.left = startX + 'px'; w.style.top = '30px'; document.getElementById('container').appendChild(w); let startTime = performance.now(); function animate(time) { let progress = (time - startTime) / 2000; let y = progress * 160; let x = startX + Math.sin(progress * Math.PI * 6) * 30; if (progress > 0.7) x = x + (100 - x) * ((progress - 0.7) * 3.33); w.style.transform = `translate(${x - startX}px, ${y}px)`; w.style.opacity = progress < 0.2 ? progress * 5 : progress > 0.8 ? (1 - progress) * 5 : 1; if (progress < 1) requestAnimationFrame(animate); else w.remove(); } requestAnimationFrame(animate); }
        function flushIt() { if(recognition) recognition.stop(); bin.classList.remove('open'); isOpen = false; document.getElementById('boomSound').play(); setTimeout(() => document.getElementById('flushSound').play(), 600); document.body.animate([ { transform: 'translate(5px, 5px)' }, { transform: 'translate(-5px, -5px)' }, { transform: 'translate(0px, 0px)' } ], { duration: 150, iterations: 6 }); flushBtn.style.display = "none"; statusText.innerText = "Cleared!"; setTimeout(() => statusText.innerText = "Tap bin & speak stress out", 5000); }
    </script></body></html>
    """
    st.components.v1.html(flush_html, height=270)

st.markdown("---")

# ==========================================
# 7. Cross-Question Chat Interface
# ==========================================
if st.session_state.analysis_done:
    st.markdown("<h2 class='glow-title' style='font-size: 2rem; color: #ff00ff; margin-top: 50px;'>💬 Cross-Examine The AI</h2>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])

    user_chat = st.chat_input("Apne doubts yaha type kar bhai...")

    if user_chat:
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_chat)
        st.session_state.chat_history.append({"role": "user", "content": user_chat})
        
        chat_instruction = (
            "तुम्हारा नाम 'Adarsh Maurya AI' है। एकदम WhatsApp वाले short forms (thk, kya, bhi, yrr) use karo. Emoji bilkul mat lagao. "
            "Sarcasm aur jokes ka use karo. TUNE ABHI IS ACCOUNT KO ANALYZE KIYA HAI: YT: {st.session_state.yt_data}. TERA ROADMAP YE HAI: {st.session_state.ai_response}. "
            "User roadmap par sawaal puch raha hai. brutally honest aur clear reply de. Max 2-3 lines."
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
                
        if not chat_success: st.error("⚠️ AI Hang! Quota over.")
