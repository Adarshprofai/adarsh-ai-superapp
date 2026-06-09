import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image
import time

# 1. पेज का प्रीमियम डिज़ाइन
st.set_page_config(page_title="Adarsh AI Pro", page_icon="🧑‍💻", layout="wide")

# 2. मल्टीपल API Keys को लोड करना
try:
    api_keys = st.secrets["GEMINI_API_KEYS"].split(",")
except Exception as e:
    st.error("Secrets missing! Streamlit me Settings -> Secrets me jakar GEMINI_API_KEYS dalo.")
    st.stop()

if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

# 3. साइडबार
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.title("Adarsh Maurya")
    st.write("🤖 Artificial Intelligence & CS Enthusiast")
    st.markdown("---")
    
    # NAVIGATION MENU (Now with 3 Zones)
    st.subheader("Explore Zones")
    app_mode = st.radio("Select Vibe:", [
        "🤖 AI & Creative Zone", 
        "🗑️ The Mental Flush",
        "📈 AI Channel Analyzer" # NEW ZONE ADDED
    ], label_visibility="collapsed")
    st.markdown("---")
    
    st.markdown("**Connect with me:**")
    st.caption("💻 GitHub | 🌐 Instagram | 🚀 LinkedIn")


# ==========================================
# 🌌 ZONE 1: AI & CREATIVE ZONE 
# ==========================================
if app_mode == "🤖 AI & Creative Zone":
    premium_css = """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); background-size: cover; background-attachment: fixed; }
    [data-testid="stSidebar"] { background-color: rgba(10, 10, 10, 0.4) !important; backdrop-filter: blur(15px); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    h1, h2, h3, p, span, div { color: #ffffff !important; }
    [data-testid="stFileUploadDropzone"] { background-color: #ffff00 !important; border: 3px dashed #000000 !important; border-radius: 12px !important; }
    [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploadDropzone"] p { color: #000000 !important; font-weight: 800 !important; }
    [data-testid="stFileUploadDropzone"] svg { fill: #000000 !important; }
    [data-testid="stFileUploadDropzone"] button { background-color: #000000 !important; color: #ffff00 !important; border: none !important; font-weight: bold !important; }
    .stChatInputContainer { border: 2px solid #000000 !important; border-radius: 15px !important; background-color: #ffffff !important; }
    textarea { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    textarea::placeholder { color: #000000 !important; opacity: 0.9 !important; }
    [data-testid="stChatInputSubmitButton"] { color: #000000 !important; }
    [data-testid="stChatInputSubmitButton"] svg { fill: #000000 !important; }
    .stChatMessage { background-color: rgba(20, 20, 20, 0.6) !important; backdrop-filter: blur(12px) !important; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 15px; padding: 15px; margin-bottom: 15px; color: white !important; }
    </style>
    """
    st.markdown(premium_css, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.35, 0.35, 0.3])
    with col1:
        st.markdown("<h1 style='margin-top: 50px; margin-bottom: 0px;'>Adarsh Maurya AI 🤖</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #aaaaaa; font-size: 16px; font-weight: 500; font-style: italic; letter-spacing: 1.5px;'>Raw Intelligence. Unfiltered Vibe.</p>", unsafe_allow_html=True)

    with col2:
        flush_html = """
        <!DOCTYPE html><html><head><style>
        body { text-align: center; background: transparent; overflow: hidden; font-family: sans-serif; color: white; margin: 0;}
        .bin-container { position: relative; width: 100%; height: 260px; overflow: hidden; background: rgba(10,10,10,0.4); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);}
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
        <div class="bin-container" id="container"><p id="statusText">Tap dustbin & speak ur stress out</p>
        <div class="dustbin" id="bin" onclick="toggleBin()"><div class="lid"></div><div class="mic">🎙️</div></div>
        <button id="flushBtn" onclick="flushIt()">FLUSH IT</button></div>
        <audio id="boomSound" src="https://assets.mixkit.co/active_storage/sfx/119/119-preview.mp3"></audio>
        <audio id="flushSound" src="https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"></audio>
        <script>
        let bin = document.getElementById('bin'); let statusText = document.getElementById('statusText'); let flushBtn = document.getElementById('flushBtn'); let boom = document.getElementById('boomSound'); let flush = document.getElementById('flushSound'); let isOpen = false; let recognition; let wordsDropped = 0;
        if ('webkitSpeechRecognition' in window) { recognition = new webkitSpeechRecognition(); recognition.continuous = true; recognition.interimResults = false; recognition.lang = 'hi-IN'; recognition.onresult = function(event) { for (let i = event.resultIndex; i < event.results.length; ++i) { if (event.results[i].isFinal) { let text = event.results[i][0].transcript.trim(); let words = text.split(' '); words.forEach((w, index) => { setTimeout(() => dropWord(w), index * 300); }); wordsDropped += words.length; if(wordsDropped > 0 && isOpen) { setTimeout(() => { flushBtn.style.display = "block"; }, 1500); } } } }; }
        function toggleBin() { if(!isOpen) { bin.classList.add('open'); statusText.innerText = "Listening... Words going to trash"; statusText.style.color = "#ff6666"; isOpen = true; if(recognition) { try { recognition.start(); } catch(e){} } } else { bin.classList.remove('open'); statusText.innerText = "Bin Locked. Ready to Flush?"; statusText.style.color = "#888"; isOpen = false; if(recognition) { try { recognition.stop(); } catch(e){} } } }
        function dropWord(text) { let w = document.createElement('div'); w.className = 'word'; w.innerText = text; let startX = 20 + Math.random() * 150; w.style.left = startX + 'px'; w.style.top = '30px'; document.getElementById('container').appendChild(w); let startTime = performance.now(); function animate(time) { let progress = (time - startTime) / 2000; if (progress > 1) progress = 1; let y = progress * 160; let x = startX + Math.sin(progress * Math.PI * 6) * 30; if (progress > 0.7) { x = x + (100 - x) * ((progress - 0.7) * 3.33); } w.style.transform = `translate(${x - startX}px, ${y}px)`; if(progress < 0.2) w.style.opacity = progress * 5; else if (progress > 0.8) w.style.opacity = (1 - progress) * 5; else w.style.opacity = 1; if (progress < 1) { requestAnimationFrame(animate); } else { w.remove(); } } requestAnimationFrame(animate); }
        function flushIt() { if(recognition) recognition.stop(); bin.classList.remove('open'); isOpen = false; boom.play(); setTimeout(() => flush.play(), 600); document.body.animate([ { transform: 'translate(5px, 5px)' }, { transform: 'translate(-5px, -5px)' }, { transform: 'translate(0px, 0px)' } ], { duration: 150, iterations: 6 }); document.querySelectorAll('.word').forEach(e => e.remove()); flushBtn.style.display = "none"; statusText.innerText = "Garbage Cleared! You are light now."; statusText.style.color = "#00e5ff"; setTimeout(() => { statusText.innerText = "Tap dustbin & speak ur stress out"; statusText.style.color = "#bbb"; wordsDropped = 0; }, 5000); }
        </script></body></html>
        """
        components.html(flush_html, height=270)

    with col3:
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        game_html = """
        <!DOCTYPE html><html><head><style>canvas { border: 1px solid rgba(255,255,255,0.2); background-color: rgba(10,10,10,0.5); border-radius: 10px; cursor: pointer; display: block;} body { margin: 0; overflow: hidden; display: flex; justify-content: right;}</style></head><body>
        <canvas id="gameCanvas" width="280" height="80"></canvas>
        <script>
        const canvas = document.getElementById("gameCanvas"); const ctx = canvas.getContext("2d"); let player = { x: 30, y: 50, width: 15, height: 15, dy: 0, gravity: 0.6, jumpPower: -8, isJumping: false }; let obstacle = { x: 280, y: 50, width: 15, height: 15, dx: -4 }; let score = 0; let isGameOver = false; let gameStarted = false; let highScore = localStorage.getItem('adarshHighScore') || 0;
        function draw() { ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = "rgba(255, 255, 255, 0.7)"; ctx.font = "12px Arial"; ctx.fillText("Score: " + Math.floor(score), 10, 20); ctx.fillStyle = "rgba(255, 215, 0, 0.9)"; ctx.fillText("HI: " + Math.floor(highScore), 210, 20); if (!gameStarted) { ctx.fillStyle = "#00e5ff"; ctx.fillRect(player.x, player.y, player.width, player.height); ctx.fillStyle = "#ff003c"; ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height); ctx.fillStyle = "white"; ctx.font = "bold 16px Arial"; ctx.fillText("▶ START", 105, 45); return; } if (isGameOver) { ctx.fillStyle = "white"; ctx.font = "12px Arial"; ctx.fillText("Game Over! Tap", 95, 45); return; } ctx.fillStyle = "#00e5ff"; ctx.fillRect(player.x, player.y, player.width, player.height); ctx.fillStyle = "#ff003c"; ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height); player.y += player.dy; if (player.y < 50) { player.dy += player.gravity; } else { player.y = 50; player.dy = 0; player.isJumping = false; } obstacle.x += obstacle.dx; if (obstacle.x < -20) { obstacle.x = canvas.width; obstacle.dx -= 0.1; } score += 0.1; if (player.x < obstacle.x + obstacle.width && player.x + player.width > obstacle.x && player.y < obstacle.y + obstacle.height && player.y + player.height > obstacle.y) { isGameOver = true; if (score > highScore) { highScore = score; localStorage.setItem('adarshHighScore', highScore); } } requestAnimationFrame(draw); }
        function jump(e) { if(e && e.type === "keydown" && e.code !== "Space") return; if (e && e.type === "keydown") e.preventDefault(); if (!gameStarted) { gameStarted = true; draw(); return; } if (!player.isJumping && !isGameOver) { player.dy = player.jumpPower; player.isJumping = true; } else if (isGameOver) { obstacle.x = canvas.width; obstacle.dx = -4; score = 0; isGameOver = false; draw(); } } window.addEventListener("keydown", jump); canvas.addEventListener("mousedown", jump); canvas.addEventListener("touchstart", jump); draw(); 
        </script></body></html>
        """
        components.html(game_html, height=100)

    st.markdown("---")
    st.markdown("### ✨ Shayari ke liye Photo dalein")
    up_col1, up_col2 = st.columns([0.35, 0.65]) 
    with up_col1: uploaded_photo = st.file_uploader("➕ Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if uploaded_photo is not None:
        img = Image.open(uploaded_photo)
        p_col1, p_col2 = st.columns([0.2, 0.8])
        with p_col1: st.image(img, caption="Vibe Check...", use_column_width=True)
        with p_col2:
            with st.spinner("tasveer ko padh kar vibe samajh raha hu..."):
                shayari_prompt = "1. Pyaara compliment do. 2. Space chhod kar, 2-4 line ki aasan Hindi me Urdu words (sukoon, noor) mix karke deep shayari likho. Text Devnagari me ho."
                success = False
                for _ in range(len(api_keys)):
                    try:
                        client = genai.Client(api_key=api_keys[st.session_state.current_key_index])
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=[img, shayari_prompt])
                        st.markdown(f"<div style='background: rgba(15,15,15,0.6); padding: 30px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); text-align: center; font-family: Georgia, serif; font-size: 2.0rem; font-weight: 500; color: #f1f5f9;'><i>{response.text.replace(chr(10), '<br>')}</i></div>", unsafe_allow_html=True)
                        success = True
                        break
                    except Exception:
                        st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
                if not success: st.error("API limit khatam.")

    st.markdown("---")
    system_instruction = "तुम्हारा नाम 'Adarsh Maurya AI' है। एकदम WhatsApp वाले short forms (thk, kya, bhi, yrr) use karo. Emoji bilkul mat lagao. Sarcasm aur jokes ka use karo. Conversation ko aage badhao. Maximum 1-3 lines me reply do."
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar): st.markdown(msg["content"])
    user_input = st.chat_input("yaha type kr bhai...")
    if user_input:
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        chat_success = False
        for _ in range(len(api_keys)):
            try:
                client = genai.Client(api_key=api_keys[st.session_state.current_key_index])
                response = client.models.generate_content(model='gemini-2.5-flash', contents=user_input, config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7))
                with st.chat_message("assistant", avatar="🤖"): st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                chat_success = True
                break
            except Exception:
                st.session_state.current_key_index = (st.session_state.current_key_index + 1) % len(api_keys)
        if not chat_success: st.error("Quota Over! Bhai aaj ki limit khatam ho gayi.")

# ==========================================
# 🗑️ ZONE 2: THE MENTAL FLUSH 
# ==========================================
elif app_mode == "🗑️ The Mental Flush":
    flush_css = """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: rgba(10, 10, 10, 0.6) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(255, 255, 255, 0.05); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .flush-title { text-align: center; font-family: 'Courier New', monospace; font-size: 3rem; color: #444; text-shadow: 0 0 10px rgba(255,255,255,0.1); margin-bottom: 0px;}
    .flush-sub { text-align: center; color: #666; font-size: 1.2rem; margin-top: -10px; margin-bottom: 30px;}
    </style>
    """
    st.markdown(flush_css, unsafe_allow_html=True)
    st.markdown("<h1 class='flush-title'>THE MENTAL FLUSH</h1>", unsafe_allow_html=True)
    st.markdown("<p class='flush-sub'>Dump your mental garbage here. No one is judging.</p>", unsafe_allow_html=True)
    
    # Original Mental Flush Code here...
    st.info("The Mental Flush feature is active. (Code hidden for brevity in this snippet to focus on Zone 3, paste your original Zone 2 HTML here if needed)")

# ==========================================
# 📈 ZONE 3: AI CHANNEL ANALYZER (NEW!!!)
# ==========================================
elif app_mode == "📈 AI Channel Analyzer":
    
    # Sleek Hacker/Data Scientist CSS
    analyzer_css = """
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {
        background-color: #0a0e17; 
        color: #e0e6ed;
    }
    [data-testid="stSidebar"] { background-color: rgba(10, 10, 10, 0.8) !important; backdrop-filter: blur(15px); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    .glow-title {
        text-align: center; font-family: 'Courier New', monospace; font-size: 2.5rem; 
        color: #00ffcc; text-shadow: 0 0 15px rgba(0, 255, 204, 0.5); margin-bottom: 10px;
    }
    .sub-title { text-align: center; color: #8892b0; font-size: 1.1rem; margin-top: -10px; margin-bottom: 40px;}
    
    /* Input Boxes */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #00ffcc !important;
        color: #00ffcc !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Loading Text Matrix Style */
    .matrix-text {
        font-family: 'Courier New', Courier, monospace;
        color: #00ffcc;
        font-size: 1.2rem;
        text-align: center;
        text-shadow: 0 0 5px #00ffcc;
        margin-top: 30px;
        margin-bottom: 30px;
    }
    
    /* Output Cards */
    .blueprint-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00ffcc;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """
    st.markdown(analyzer_css, unsafe_allow_html=True)
    
    st.markdown("<h1 class='glow-title'>AI CHANNEL ANALYZER</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Stop guessing. Let AI decode your algorithm.</p>", unsafe_allow_html=True)
    
    # 🟢 STEP 1: The Input Zone
    col1, col2 = st.columns(2)
    with col1:
        yt_link = st.text_input("🔗 YouTube Channel URL", placeholder="https://youtube.com/@yourchannel")
    with col2:
        ig_username = st.text_input("📸 Instagram Username", placeholder="@yourusername")
        
    analyze_button = st.button("🚀 Analyze My Digital Identity", use_container_width=True)
    st.markdown("---")
    
    # 🟢 STEP 2 & 3: The Cinematic Fake Loading & Output
    if analyze_button and (yt_link or ig_username):
        
        # The Hacker Loading Sequence
        status_placeholder = st.empty()
        loading_messages = [
            "Initializing connection to YouTube Data API...",
            "Scraping latest 50 video metrics & thumbnails...",
            "Bypassing Instagram limits for engagement patterns...",
            "Analyzing audience retention and drop-off graphs...",
            "Cross-referencing multi-platform performance...",
            "Drafting the 30-Day Masterplan..."
        ]
        
        for msg in loading_messages:
            status_placeholder.markdown(f"<div class='matrix-text'>⚡ {msg}</div>", unsafe_allow_html=True)
            time.sleep(1.5) # The 2-minute cinematic illusion (shortened for testing)
            
        status_placeholder.empty() # Clear loading text
        
        # 🟢 STEP 4: The Placeholder Output (Dummy Data showing real vibes)
        st.success("✅ Analysis Complete! Here is your personalized Blueprint.")
        
        st.markdown("""
        <div class='blueprint-card'>
            <h3 style='color: #ff4d4d;'>🚨 1. The Brutal Truth</h3>
            <p>Your mixed content strategy is causing algorithm confusion. Tutorials and coding shorts get <strong>low retention (22%)</strong>, but when you speak raw and authentically on camera, your engagement spikes by <strong>400%</strong>.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='blueprint-card'>
            <h3 style='color: #ffd700;'>🎯 2. The Golden Niche</h3>
            <p>Data shows massive audience interest in authentic, raw stories about personal transformation. Your journey from being an <strong>introvert to an extrovert</strong> resonates deeply. Stick strictly to this mindset and self-improvement niche. Use cinematic or raw minimalist aesthetics in CapCut—avoid over-editing.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='blueprint-card'>
            <h3 style='color: #00ffcc;'>⏱️ 3. Timing & Frequency Strategy</h3>
            <ul>
                <li><strong>YouTube:</strong> 1 Long-form video (8-10 mins) every Sunday at 11:30 AM.</li>
                <li><strong>Instagram Reels:</strong> 4 times a week (Mon, Wed, Fri, Sat) strictly between 6:30 PM - 8:00 PM.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
