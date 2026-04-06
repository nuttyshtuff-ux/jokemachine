import streamlit as st
import google.generativeai as genai

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

# 2. API SETUP
api_key = st.secrets.get("api_key")
if not api_key:
    st.error("Check your Streamlit Secrets for the 'api_key'!"); st.stop()

genai.configure(api_key=api_key)

RATING_OPTIONS = {1: "G", 2: "PG", 3: "PG-13", 4: "R"}
STYLES = ["Pun", "Riddle", "Observational", "Insult", "Self-Deprecating", "Weird", "Urban", "Latino", "Anecdote"]

# 3. SIDEBAR
with st.sidebar:
    st.header("📝 WRITER CONTROLS")
    v_score = st.select_slider("Rating", options=[1, 2, 3, 4], value=3, format_func=lambda x: RATING_OPTIONS.get(x))
    sel_s = [s for s in STYLES if st.checkbox(s, key=f"s_{s}")]
    num_jokes = st.number_input("How many?", min_value=1, max_value=10, value=3)
    if "last_res" in st.session_state:
        st.download_button("💾 DOWNLOAD", st.session_state["last_res"], "jokes.txt", use_container_width=True)

# 4. MAIN UI
paypal_url = "https://www.paypal.me/YOUR_USERNAME" 
st.markdown(f"<div class='main-title'><h1>📝 THE JOKE WRITER</h1><a href='{paypal_url}' target='_blank' class='header-support'>💰 Support the Comic</a></div>", unsafe_allow_html=True)
subject = st.text_area("Topic/Joke:", height=250, placeholder="e.g. Cancer Awareness")

# 5. RUN LOGIC
if st.button("🚀 WRITE JOKES", use_container_width=True):
    if subject:
        prompt = f"Act as a professional comedy writer. Rating: {RATING_OPTIONS[v_score]}. Style: {', '.join(sel_s)}. Topic: {subject}. Generate {num_jokes} jokes."
        try:
            with st.spinner("Writing..."):
                # Using the cleanest possible model name
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.session_state["last_res"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"🚨 Connection Error: {e}")
    else:
        st.warning("Enter a topic!")

# 6. DISPLAY
if "last_res" in st.session_state:
    st.markdown(f"<div class='response-card'>### 🎙️ The Suggestions:\n\n{st.session_state['last_res']}</div>", unsafe_allow_html=True)
