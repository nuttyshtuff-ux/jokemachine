import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="The Joke Writer", page_icon="📝", layout="wide")

# 1. CSS - Navy & Yellow Aesthetic
st.markdown("""<style>
    .main-title { 
        color: #1e3a8a; font-weight: 800; text-align: center; 
        border: 3px solid #1e3a8a; padding: 20px; border-radius: 20px; 
        background-color: #f8fbff; margin-bottom: 30px;
    }
    .header-support {
        display: inline-block; margin-top: 15px; background-color: #facc15;
        color: #1e3a8a !important; padding: 8px 20px; border-radius: 10px;
        font-weight: bold; text-decoration: none; border: 2px solid #1e3a8a; font-size: 14px;
    }
    .stButton button { background-color: #facc15 !important; color: #1e3a8a !important; border: 2px solid #1e3a8a !important; font-weight: bold !important; border-radius: 12px !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a; }
    [data-testid="stSidebar"] * { color: #fef08a !important; }
    .joke-card { background-color: #f8fbff; border-left: 8px solid #facc15; padding: 20px; border-radius: 10px; color: #1e3a8a; margin-bottom: 15px; border: 1px solid #1e3a8a; }
</style>""", unsafe_allow_html=True)

# 2. API SETUP (Corrected for google-generativeai)
api_key = st.secrets.get("api_key")
if not api_key:
    st.error("Missing API Key in Secrets!"); st.stop()
genai.configure(api_key=api_key)

# 3. SIDEBAR CONTROLS
with st.sidebar:
    st.header("⚙️ WRITER SETTINGS")
    rating_map = {1: "G (Clean)", 2: "PG (Mild)", 3: "PG-13 (Edgy)", 4: "R (Adult)"}
    sel_rating = st.select_slider("Content Rating", options=[1, 2, 3, 4], value=2, format_func=lambda x: rating_map[x])
    
    st.subheader("Joke Styles")
    styles = ["Pun", "Riddle", "Observational", "Insult", "Self-Deprecating", "Weird/Offbeat", "Urban/HipHop", "Latino", "Anecdote"]
    sel_styles = [s for s in styles if st.checkbox(s, key=f"s_{s}")]
    
    st.subheader("Mode")
    extend_mode = st.checkbox("Extend this Joke")
    num_jokes = st.number_input("Number of Suggestions", min_value=1, max_value=10, value=3)
    
    st.markdown("---")
    if "joke_output" in st.session_state:
        st.download_button("💾 SAVE JOKES", st.session_state["joke_output"], "jokes.txt", use_container_width=True)

# 4. MAIN UI
paypal_url = "https://www.paypal.me/YOUR_USERNAME" 
st.markdown(f"""
    <div class='main-title'>
        <h1>📝 THE JOKE WRITER</h1>
        <a href="{paypal_url}" target="_blank" class="header-support">💰 Support the Comic</a>
    </div>
""", unsafe_allow_html=True)

subject = st.text_area("Input Subject or Existing Joke:", height=200, placeholder="Enter a topic or paste a joke...")

# 5. GENERATION LOGIC (Corrected Syntax)
if st.button("✨ WRITE JOKES", use_container_width=True):
    if not subject:
        st.warning("Please enter a subject!")
    else:
        rating_text = rating_map[sel_rating]
        style_list = ", ".join(sel_styles)
        
        prompt = f"Act as a professional comedy writer. Rating: {rating_text}. Styles: {style_list}. Subject: {subject}. Generate {num_jokes} jokes."
        if extend_mode:
            prompt += " Take the input as a setup and write tags or alternative punchlines."

        try:
            with st.spinner("Writing..."):
                # Using the 'gemini-1.5-flash' name with the correct library call
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.session_state["joke_output"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# 6. DISPLAY RESULTS
if "joke_output" in st.session_state:
    st.markdown("### 🎙️ The Writers' Room Suggests:")
    st.markdown(f"<div class='joke-card'>{st.session_state['joke_output']}</div>", unsafe_allow_html=True)
