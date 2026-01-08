import streamlit as st
import os
import pandas as pd
import time
import tempfile
import shutil
# Import local modules

from matching import find_matching_resumes_by_similarity
from db import init_db, get_db_connection

# Page Config
st.set_page_config(
    page_title="AI Resume Matcher", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database on Startup
if "db_ready" not in st.session_state:
    init_db()
    st.session_state.db_ready = True

# Theme Management
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

# Define Theme Colors
themes = {
    'dark': {
        'bg_color': '#0e1117',
        'card_bg': '#262730',
        'text_primary': '#FAFAFA',
        'text_secondary': '#E0E0E0',
        'badge_bg': '#31333F',
        'badge_text': '#FAFAFA',
        'badge_border': '#464B5C',
        'shadow': 'rgba(0,0,0,0.3)',
        'shadow_hover': 'rgba(0,0,0,0.5)'
    },
    'light': {
        'bg_color': '#f8f9fa',
        'card_bg': '#ffffff',
        'text_primary': '#1a1a1a',
        'text_secondary': '#555555',
        'badge_bg': '#f0f2f6',
        'badge_text': '#31333F',
        'badge_border': '#e0e0e0',
        'shadow': 'rgba(0,0,0,0.1)',
        'shadow_hover': 'rgba(0,0,0,0.15)'
    }
}

current_theme = themes[st.session_state.theme]

# Custom CSS for modern styling
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    .main {{
        background-color: {current_theme['bg_color']};
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }}
    .css-1d391kg {{
        padding-top: 2rem;
    }}
    .match-card {{
        background-color: {current_theme['card_bg']};
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px {current_theme['shadow']};
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
        transition: transform 0.2s;
        color: {current_theme['text_primary']};
    }}
    .match-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px {current_theme['shadow_hover']};
    }}
    .score-badge {{
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
    }}
    .role-badge {{
        background-color: {current_theme['badge_bg']};
        color: {current_theme['badge_text']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        margin-right: 5px;
        border: 1px solid {current_theme['badge_border']};
    }}
    h1 {{
        color: {current_theme['text_primary']};
    }}
    h3 {{
        color: {current_theme['text_primary']} !important;
    }}
    p {{
        color: {current_theme['text_secondary']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Resume Matcher")
    
    # 1. Browse/Upload Section (Moved to Top)
    st.markdown("### <i class='fa-solid fa-file-arrow-up'></i> Upload Resumes", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drop PDF/DOCX files here", 
        accept_multiple_files=True, 
        type=['pdf', 'docx', 'doc']
    )
    
    if uploaded_files:
        if st.button("Process Files", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create a temporary directory for this session's uploads
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save files
                status_text.text("Saving files...")
                    
                for i, uploaded_file in enumerate(uploaded_files):
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    progress_bar.progress((i + 1) / len(uploaded_files) * 0.5)
                
                # Process files
                status_text.text("Parsing & Indexing...")
                try:
                    from resume_parser import process_all_resumes
                    conn = get_db_connection()
                    process_all_resumes(conn, resume_folder=temp_dir)
                    conn.close()
                    progress_bar.progress(1.0)
                    st.success(f"Successfully processed {len(uploaded_files)} resumes!")
                    time.sleep(2)
                    status_text.empty()
                    progress_bar.empty()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.markdown("---")
    
    # 2. Settings Section
    st.markdown("### <i class='fa-solid fa-sliders'></i> Settings", unsafe_allow_html=True)
    top_n = st.number_input("Max Matches", min_value=1, max_value=200, value=5, step=1)
    
    st.markdown("---")

    # 3. Theme Toggle (Moved to Bottom)
    st.button(
        "Toggle Theme", 
        on_click=toggle_theme,
        help="Switch between Dark and Light mode"
    )

# Main Content
st.title("Smart Resume Screening")
st.markdown("### Find the perfect candidate in seconds using AI.")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### <i class='fa-solid fa-file-lines'></i> Job Description", unsafe_allow_html=True)
    default_jd = """We are looking for a Senior Machine Learning Engineer with experience in:
- Natural Language Processing (NLP) and LLMs
- Python, PyTorch, and TensorFlow
- Deploying models to production (AWS/GCP)
- 3+ years of experience"""
    
    jd_input = st.text_area(
        "Paste the Job Description (JD) here", 
        value=default_jd, 
        height=300,
        help="Paste the full job description text here to find matching resumes."
    )

with col2:
    st.markdown("### <i class='fa-solid fa-filter'></i> Matching Controls", unsafe_allow_html=True)
    st.markdown("""
    Click the button below to analyze all indexed resumes against the provided job description.
    
    The system uses **semantic search** to find candidates who match the *meaning* of the requirements, not just keywords.
    """)
    if st.button("Find Top Matches", type="primary"):
        run_search = True
    else:
        run_search = False

st.markdown("---")

# Results Section
if run_search:
    if not jd_input.strip():
        st.warning("⚠️ Please enter a Job Description first.")
    else:
        with st.spinner("🧠 Analyzing resumes and calculating compatibility scores..."):
            try:
                conn = get_db_connection()
                results = find_matching_resumes_by_similarity(jd_input, conn, top_n)
                conn.close()
                
                if not results:
                    st.warning("No matches found. Try uploading some resumes first!")
                else:
                    st.success(f"Found {len(results)} matches")
                    
                    for i, res in enumerate(results, 1):
                        score = res['similarity_score']
                        score_pct = f"{score*100:.1f}%"
                        
                        # Color coding for score
                        if score > 0.4:
                            border_color = "#4CAF50" # Green
                        elif score > 0.25:
                            border_color = "#FF9800" # Orange
                        else:
                            border_color = "#F44336" # Red
                            
                        # Card HTML
                        st.markdown(f"""
                        <div class="match-card" style="border-left: 5px solid {border_color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin: 0; color: {current_theme['text_primary']};">#{i} {res['name']}</h3>
                                <div class="score-badge" style="background-color: {border_color};">{score_pct} Match</div>
                            </div>
                            <p style="color: {current_theme['text_secondary']}; margin-top: 5px;">
                                <span class="role-badge"><i class="fa-solid fa-location-dot"></i> {res['location']}</span>
                                <span class="role-badge"><i class="fa-solid fa-briefcase"></i> {res['current_job_title']}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Details Expander
                        with st.expander(f"View Profile Details for {res['name']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"#### <i class='fa-solid fa-tools'></i> Skills", unsafe_allow_html=True)
                                skills = res['skills'] or []
                                st.write(", ".join(skills))
                                
                                st.markdown(f"#### <i class='fa-solid fa-graduation-cap'></i> Education", unsafe_allow_html=True)
                                for edu in res['education'] or []:
                                    st.write(f"• **{edu.get('degree', 'Degree')}** in {edu.get('field', 'Field')}")
                                    st.caption(f"{edu.get('institution', 'Institution')}")

                            with c2:
                                st.markdown(f"#### <i class='fa-solid fa-briefcase'></i> Experience", unsafe_allow_html=True)
                                for exp in res['experience'] or []:
                                    st.write(f"• **{exp.get('title', 'Role')}** at {exp.get('company', 'Company')}")
                                    st.caption(exp.get('description', '')[:150] + "...")
                                    
            except Exception as e:
                st.error(f"Error during matching: {str(e)}")
