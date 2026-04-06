import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="The Joke Writer", page_icon="📝", layout="wide")

# 1. CSS - Consistent Navy & Yellow Aesthetic
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

# 2. API SETUP
api_key = st.secrets.get("api_key")
if not api_key:
    st.error("Missing API Key in Secrets!"); st.stop()
client = genai.Client(api_key=api_key)

# 3. SIDEBAR CONTROLS
with st.sidebar:
    st.header("⚙️ WRITER SETTINGS")
    
    # Rating Slider
    rating_map = {1: "G (Clean/Family)", 2: "PG (Mild)", 3: "PG-13 (Edgy)", 4: "R (Raw/Adult)"}
    sel_rating = st.select_slider("Content Rating", options=[1, 2, 3, 4], value=2, format_func=lambda x: rating_map[x])
    
    st.subheader("Joke Styles")
    styles = ["Pun", "Riddle", "Observational", "Insult", "Self-Deprecating", "Weird/Offbeat", "Urban/HipHop", "Latino", "Anecdote"]
    sel_styles = [s for s in styles if st.checkbox(s, key=f"s_{s}")]
    
    st.subheader("Mode")
    extend_mode = st.checkbox("Extend this Joke", help="Check this if you are pasting an existing joke to get related material.")
    
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

subject = st.text_area("Input Subject or Existing Joke:", height=200, placeholder="e.g., '7th graders', 'coffee', or paste a joke to extend it...")

# 5. GENERATION LOGIC
if st.button("✨ WRITE JOKES", use_container_width=True):
    if not subject:
        st.warning("Please enter a subject or joke!")
    elif not sel_styles and not extend_mode:
        st.warning("Please select at least one style!")
    else:
        # Prompt Engineering
        mode_text = "EXTEND" if extend_mode else "CREATE"
        rating_text = rating_map[sel_rating]
        style_list = ", ".join(sel_styles)
        
        prompt = f"Act as a professional comedy writer. Mode: {mode_text}. Rating: {rating_text}. "
        prompt += f"Styles requested: {style_list}. Subject/Input: {subject}. "
        prompt += f"Generate exactly {num_jokes} jokes. Format each joke clearly with a 'Style' label."
        
        if extend_mode:
            prompt += " Look at the provided joke and write related tags, alternative punchlines, or 'next-step' jokes in the requested styles."

        try:
            with st.spinner("Brainstorming in the Writers' Room..."):
                res = client.models.generate_content(model="gemini-2.0-flash-001", contents=prompt)
                st.session_state["joke_output"] = res.text
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# 6. DISPLAY RESULTS
if "joke_output" in st.session_state:
    st.markdown("### 🎙️ The Writers' Room Suggests:")
    jokes = st.session_state["joke_output"]
    st.markdown(f"<div class='joke-card'>{jokes}</div>", unsafe_allow_html=True)
