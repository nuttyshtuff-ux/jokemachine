import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="The Joke Writer", page_icon="📝", layout="wide")

# 1. CSS
st.markdown("""<style>
    .main-title { color: #1e3a8a; font-weight: 800; text-align: center; border: 3px solid #1e3a8a; padding: 20px; border-radius: 20px; background-color: #f8fbff; margin-bottom: 30px; }
    .header-support { display: inline-block; margin-top: 15px; background-color: #facc15; color: #1e3a8a !important; padding: 8px 20px; border-radius: 10px; font-weight: bold; text-decoration: none; border: 2px solid #1e3a8a; font-size: 14px; }
    .stButton button { background-color: #facc15 !important; color: #1e3a8a !important; border: 2px solid #1e3a8a !important; font-weight: bold !important; border-radius: 12px !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a; }
    [data-testid="stSidebar"] * { color: #fef08a !important; }
    .response-card { background-color: #eff6ff; border-left: 8px solid #facc15; padding: 20px; border-radius: 10px; color: #1e3a8a; white-space: pre-wrap; }
</style>""", unsafe_allow_html=True)

# 2. DATA & API - FORCING V1 VERSION
api_key = st.secrets.get("api_key")
if not api_key:
    st.error("Missing API Key!"); st.stop()

# This is the "Magic Fix": We tell the client exactly which API version to use
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

STYLES = ["Pun", "Riddle", "Observational", "Insult", "Self-Deprecating", "Weird/Offbeat", "Urban/HipHop", "Latino", "Anecdote"]
RATING_OPTIONS = {1: "G", 2: "PG", 3: "PG-13", 4: "R"}

# 3. SIDEBAR
with st.sidebar:
    st.header("📝 WRITER CONTROLS")
    v_score = st.select_slider("Rating", options=[1, 2, 3, 4], value=2, format_func=lambda x: RATING_OPTIONS.get(x))
    sel_s = [s for s in STYLES if st.checkbox(s, key=f"s_{s}")]
    num_jokes = st.number_input("How many?", min_value=1, max_value=10, value=3)
    ex = st.checkbox("Extend Joke")
    st.markdown("---")
    if "last_res" in st.session_state:
        st.download_button("💾 DOWNLOAD", st.session_state["last_res"], "jokes.txt", use_container_width=True)

# 4. MAIN UI
paypal_url = "https://www.paypal.me/YOUR_USERNAME" 
st.markdown(f"<div class='main-title'><h1>📝 THE JOKE WRITER</h1><a href='{paypal_url}' target='_blank' class='header-support'>💰 Support the Comic</a></div>", unsafe_allow_html=True)
subject = st.text_area("Topic/Joke:", height=250)

# 5. RUN LOGIC 
if st.button("🚀 WRITE JOKES", use_container_width=True):
    if subject:
        p = f"Professional Comedy Writer. Rating: {RATING_OPTIONS[v_score]}. Count: {num_jokes}. Styles: {', '.join(sel_s)}. Subject: {subject}."
        
        # Using the most universally recognized names
        m_list = ["gemini-2.0-flash", "gemini-pro"]
        
        last_error = "Init"
        success = False
        for m_name in m_list:
            if not success:
                try:
                    with st.spinner(f"Trying {m_name}..."):
                        res = client.models.generate_content(model=m_name, contents=p)
                        st.session_state["last_res"] = f"--- JOKES ---\n\n{res.text}"
                        success = True
                        st.rerun()
                except Exception as e:
                    last_error = str(e)
                    continue
        if not success:
            st.error(f"🚨 FAILED. Raw Error: {last_error}")
    else:
        st.warning("Enter a topic!")

# 6. DISPLAY
if "last_res" in st.session_state:
    display_text = st.session_state["last_res"].split("--- JOKES ---")[-1]
    st.markdown(f"<div class='response-card'><h3>🎙️ Suggestions:</h3>{display_text}</div>", unsafe_allow_html=True)
