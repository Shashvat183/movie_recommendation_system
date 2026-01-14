import streamlit as st
import pickle
import pandas as pd
import requests
import base64
import os

# Set page to wide mode
st.set_page_config(layout="wide", page_title="MovieFlix - Future of Entertainment")

# --- LOAD IMAGE ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Use Liquid Metal as the Hero Object
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, 'bg_option_1_liquid_1768201482028.png') 
    hero_img_b64 = get_base64_of_bin_file(img_path)
except:
    hero_img_b64 = ""

# --- CSS STYLING ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

/* Global Reset */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: white;
}}

.stApp {{
    background-color: #0b0c10;
}}

/* Navbar Styling */
.navbar {{
    display: flex;
    justify-content: flex-end;
    gap: 30px;
    padding: 20px 40px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #c5c6c7;
    margin-bottom: 40px;
}}
.nav-item {{
    cursor: pointer;
    transition: color 0.2s;
}}
.nav-item:hover {{
    color: white;
}}
.nav-btn {{
    border: 1px solid #45a29e;
    color: #45a29e;
    padding: 8px 16px;
    border-radius: 5px;
    text-decoration: none;
}}

/* Hero Section */
h1 {{
    font-size: 4.5rem !important;
    font-weight: 400;
    line-height: 1.1;
    margin-bottom: 20px;
    color: white;
}}
.highlight-green {{
    color: #66fcf1;
    font-weight: 400;
}}

.subtitle {{
    font-size: 1.1rem;
    color: #888;
    line-height: 1.6;
    max-width: 500px;
    margin-bottom: 40px;
}}

/* Hero Image */
.hero-img-container {{
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
}}
.hero-img {{
    width: 90%;
    max-width: 600px;
    border-radius: 20px;
    mask-image: radial-gradient(circle, black 60%, transparent 100%);
    animation: float 6s ease-in-out infinite;
}}

@keyframes float {{
	0% {{ transform: translatey(0px); }}
	50% {{ transform: translatey(-15px); }}
	100% {{ transform: translatey(0px); }}
}}
</style>

<!-- Navbar -->
<div class="navbar">
    <span class="nav-item">Genrefy</span>
    <span class="nav-item">Discovery</span>
    <span class="nav-item">AI Models</span>
    <span class="nav-item">Login</span>
    <a href="#" class="nav-btn">Start Free Trial</a>
</div>
""", unsafe_allow_html=True)

# --- HERO SECTION LAYOUT ---
col1, col2 = st.columns([1, 1.1])

with col1:
    st.markdown("<div style='height: 50px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <h1>Welcome to the<br>
    future of<br>
    <span class="highlight-green">Entertainment</span></h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p class="subtitle">
        Our machine learning technology and experienced algorithms keep your 
        watch-list up-to-date and transform your data into actionable 
        viewing intelligence - all at the touch of a button.
    </p>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 LAUNCH RECOMMENDATION APP"):
        st.session_state['show_app'] = True

with col2:
    if hero_img_b64:
        st.markdown(f"""
        <div class="hero-img-container">
             <img src="data:image/png;base64,{hero_img_b64}" class="hero-img">
        </div>
        """, unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
if st.session_state.get('show_app'):
    st.markdown("---")
    st.markdown("### 🎬 Discover Your Next Favorite")
    
    try:
        movie_list = pickle.load(open('models/movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movie_list)
        similarity = pickle.load(open('models/similarity.pkl', 'rb'))
        
        selected_movie = st.selectbox("Search for a movie...", movies['title'].values)
        
        if st.button("Recommend Movies"):
            st.session_state['recommend_clicked'] = True
            st.session_state['selected_movie'] = selected_movie
            
    except FileNotFoundError:
        st.error("Model files missing. Please run dataprep.py")

# --- RECOMMENDATION RESULTS ---
def fetch_poster(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return "https://via.placeholder.com/500x750?text=No+Poster"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

if st.session_state.get('recommend_clicked') and st.session_state.get('selected_movie'):
    st.markdown("### ✨ Your Personalized Picks")
    
    idx = movies[movies['title'] == st.session_state['selected_movie']].index[0]
    distances = similarity[idx]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            movie_id = movies.iloc[movies_list[i][0]].movie_id
            poster = fetch_poster(movie_id)
            title = movies.iloc[movies_list[i][0]].title
            
            st.image(poster)
            st.caption(title)
