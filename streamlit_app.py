import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="The Joke Writer", page_icon="📝", layout="wide")

# 1. CSS - Navy & Yellow + Header Support Button (Identical to Sim)
st.markdown("""<style>
    .main-title { 
        color: #1e3a8a; font-weight: 800; text-align: center; 
        border: 3px solid #1e3a8a; padding: 20px; border-radius: 20px; 
        background-color: #f8fbff; margin-bottom: 30px;
    }
    .header-support {
        display: inline-block;
        margin-top: 15px;
        background-color: #facc15;
        color: #1e3a8a !important;
        padding: 8px 20px;
        border-radius: 10px;
        font-weight: bold;
        text-decoration: none;
        border: 2px solid #1e3a8a;
        font-size: 14px;
    }
    .header-support:hover {
        background-color: #fde047;
        text-decoration: none;
    }
    .mic-container { display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 0.8; margin-right: 10px; }
    .mic-head { font-size: 24px; margin-bottom: -2px; }
    .mic-pole { background-color: #facc15; width: 3px; height: 12px; margin-bottom: -1px; }
    .mic-base { background-color: #facc15; width: 14px; height: 3px; border-radius: 2px; }
    .sidebar-header { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .stButton button { background-color: #facc15 !important; color: #1e3a8a !important; border: 2px solid #1e3a8a !important; font-weight: bold !important; border-radius: 12px !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a; }
    [data-testid="stSidebar"] * { color: #fef08a !important; }
    [data-testid="stWidgetLabel"] svg {
        filter: invert(86%) sepia(87%) saturate(356%) hue-rotate(352deg) brightness(102%) contrast(104%) !important;
    }
    .response-card { background-color: #eff6ff; border-left: 8px solid #facc15; padding: 20px; border-radius: 10px; color: #1e3a8a; white-space: pre-wrap; }
</style>""", unsafe_allow_html=True)

# 2. DATA
api_key = st.secrets.get("api_key")
if not api_key:
    st.error("Missing API Key!"); st.stop()
client = genai.Client(api_key=api_key)

# Joke Styles
STYLES = ["Pun", "Riddle", "Observational", "Insult", "Self-Deprecating", "Weird/Offbeat", "Urban/HipHop", "Latino", "Anecdote"]

# 3. SIDEBAR
with st.sidebar:
    st.markdown("""<div class="sidebar-header"><div class="mic-container">
    <div class="mic-head">📝</div><div class="mic-pole"></div><div class="mic-base"></div>
    </div><h3 style="margin:0;">WRITER CONTROLS</h3></div>""", unsafe_allow_html=True)
    st.success("✅ GUEST ACCESS ACTIVE")
    
    st.subheader("Rating")
    r_map = {1:"G", 2:"PG", 3:"PG-13", 4:"R"}
    v_score = st.slider("Clean <-> Raw", 1, 4, 2, format_func=lambda x: r_map[x])
    
    st.subheader("Joke Styles")
    sel_s = [s for s in STYLES if st.checkbox(s, key=f"s_{s}")]
    
    st.subheader("Options")
    num_jokes = st.number_input("Number of Jokes", min_value=1, max_value=10, value=3)
    ex = st.checkbox("Extend this Joke", help="Use input as a setup and write related tags/punchlines.")
    
    st.markdown("---")
    
    if "last_res" in st.session_state:
        st.download_button("💾 DOWNLOAD JOKES", st.session_state["last_res"], "jokes.txt", use_container_width=True)
    else:
        st.button("💾 Save (Run First)", disabled=True, use_container_width=True)

# 4. MAIN UI
paypal_url = "https://www.paypal.me/YOUR_USERNAME" 
st.markdown(f"""
    <div class='main-title'>
        <h1>📝 THE JOKE WRITER</h1>
        <a href="{paypal_url}" target="_blank" class="header-support">💰 Support the Comic</a>
    </div>
""", unsafe_allow_html=True)

instr = "Enter a subject (e.g., '7th grade girls') or an existing joke to extend."
subject = st.text_area("Your Subject/Joke:", height=300, placeholder=instr)

# 5. RUN LOGIC (Same loop and error handling as your working code)
if st.button("🚀 WRITE JOKES", use_container_width=True):
    if subject and (sel_s or ex):
        rating_text = r_map[v_score]
        
        # Crafting the Writer Prompt
        p = f"Act as a professional comedy writer. Rating: {rating_text}. Generate {num_jokes} jokes. "
        if sel_s: p += f"Styles to use: {', '.join(sel_s)}. "
        p += f"Subject/Input: {subject}. "
        
        if ex:
            p += "The input is a joke. Write related tags, alternative punchlines, and 'next-step' jokes based on it. "
        else:
            p += "Write fresh jokes based on the subject. "
            
        p += "Format each joke clearly with a label for its style."

        cfg = types.GenerateContentConfig(temperature=0.8, top_p=0.95, max_output_tokens=2000)
        m_list = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        for m_name in m_list:
            try:
                with st.spinner("Brainstorming..."):
                    res = client.models.generate_content(model=m_name, contents=p, config=cfg)
                    st.session_state["last_res"] = f"--- INPUT ---\n\n{subject}\n\n--- JOKES ---\n\n{res.text}"
                    st.rerun()
            except Exception:
                continue
    else:
        st.warning("Please provide a subject and select at least one style!")

# 6. DISPLAY
if "last_res" in st.session_state:
    display_text = st.session_state["last_res"].split("--- JOKES ---")[-1]
    st.markdown(f"""<div class='response-card'><h3>🎙️ The Writers' Room Suggests:</h3>{display_text}</div>""", unsafe_allow_html=True)
