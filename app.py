import streamlit as st
import os
import pandas as pd
import time
# Import local modules
# We need to set HF_HUB_OFFLINE=1 in env if we want to force offline, 
# but streamlit runs in its own process. We can set it at top of file.
import os
os.environ["HF_HUB_OFFLINE"] = "1"

from matching import find_matching_resumes_by_similarity

# Page Config
st.set_page_config(
    page_title="AI Resume Matcher", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .css-1d391kg {
        padding-top: 2rem;
    }
    .match-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
        transition: transform 0.2s;
    }
    .match-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .score-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
    }
    .role-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        margin-right: 5px;
    }
    h1 {
        color: #1a1a1a;
    }
    h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3850/3850285.png", width=50)
    st.title("Resume Matcher")
    st.markdown("---")
    
    st.header("⚙️ Settings")
    top_n = st.number_input("Max Matches", min_value=1, max_value=200, value=5, step=1)
    
    st.header("📂 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Drop PDF/DOCX files here", 
        accept_multiple_files=True, 
        type=['pdf', 'docx', 'doc']
    )
    
    if uploaded_files:
        if st.button("🚀 Process Uploaded Files", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save files
            status_text.text("Saving files...")
            if not os.path.exists("./resumes"):
                os.makedirs("./resumes")
                
            for i, uploaded_file in enumerate(uploaded_files):
                file_path = os.path.join("./resumes", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                progress_bar.progress((i + 1) / len(uploaded_files) * 0.5)
            
            # Process files
            status_text.text("Parsing & Indexing...")
            try:
                from resume_parser import process_all_resumes
                process_all_resumes() 
                progress_bar.progress(1.0)
                st.success(f"Successfully processed {len(uploaded_files)} resumes!")
                time.sleep(2)
                status_text.empty()
                progress_bar.empty()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")
    st.info("💡 **Tip:** Upload new resumes to update the database automatically.")

# Main Content
st.title("🚀 Smart Resume Screening")
st.markdown("### Find the perfect candidate in seconds using AI.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Job Description")
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
    st.subheader("🎯 Matching Controls")
    st.markdown("""
    Click the button below to analyze all indexed resumes against the provided job description.
    
    The system uses **semantic search** to find candidates who match the *meaning* of the requirements, not just keywords.
    """)
    if st.button("🔍 Find Top Matches", type="primary"):
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
                results = find_matching_resumes_by_similarity(jd_input, top_n)
                
                if not results:
                    st.warning("No matches found. Try uploading some resumes first!")
                else:
                    st.success(f"🎉 Found {len(results)} matches!")
                    
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
                                <h3 style="margin: 0;">#{i} {res['name']}</h3>
                                <div class="score-badge" style="background-color: {border_color};">{score_pct} Match</div>
                            </div>
                            <p style="color: #666; margin-top: 5px;">
                                <span class="role-badge">📍 {res['location']}</span>
                                <span class="role-badge">💼 {res['current_job_title']}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Details Expander
                        with st.expander(f"View Profile Details for {res['name']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("#### 🛠 Skills")
                                skills = res['skills'] or []
                                st.write(", ".join(skills))
                                
                                st.markdown("#### 🎓 Education")
                                for edu in res['education'] or []:
                                    st.write(f"• **{edu.get('degree', 'Degree')}** in {edu.get('field', 'Field')}")
                                    st.caption(f"{edu.get('institution', 'Institution')}")

                            with c2:
                                st.markdown("#### 💼 Experience")
                                for exp in res['experience'] or []:
                                    st.write(f"• **{exp.get('title', 'Role')}** at {exp.get('company', 'Company')}")
                                    st.caption(exp.get('description', '')[:150] + "...")
                                    
            except Exception as e:
                st.error(f"Error during matching: {str(e)}")
