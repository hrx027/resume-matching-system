import json
import numpy as np
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq_extractor import extract_structured_info_groq_jd
import ast

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

# Weights for different sections (can be adjusted based on importance)
SECTION_WEIGHTS = {
    "skills": 0.25,
    "experience": 0.25,
    "education": 0.15,
    "job_titles": 0.35
}

def calculate_weighted_similarity(jd_embeddings, resume_embeddings):
    """Calculate weighted average of cosine similarities"""
    total_similarity = 0
    total_weight = 0
    
    for section, weight in SECTION_WEIGHTS.items():
        if section in jd_embeddings and section in resume_embeddings:
            # Reshape for cosine_similarity
            jd_emb = jd_embeddings[section].reshape(1, -1)
            resume_emb = resume_embeddings[section].reshape(1, -1)
            
            similarity = cosine_similarity(jd_emb, resume_emb)[0][0]
            total_similarity += similarity * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0
    
    return total_similarity / total_weight

def create_jd_section_embeddings(jd_text):
    """Extract structured info from JD using GROQ and create section-wise embeddings."""
    jd_structured = extract_structured_info_groq_jd(jd_text)
    # Map JD fields to the same structure as resumes for embedding
    resume_like = {
        'current_job_title': jd_structured.get('job_title', ''),
        'preferred_job_title': '',
        'skills': jd_structured.get('required_skills', []),
        'experience': [{'title': jd_structured.get('required_experience', '')}],
        'education': [{'degree': jd_structured.get('required_education', '')}],
    }
    # Use the same embedding logic as for resumes
    embeddings = {}
    # Skills embedding
    if resume_like.get('skills'):
        skills_text = ", ".join(resume_like['skills'])
        embeddings['skills'] = model.encode(skills_text)
    else:
        embeddings['skills'] = model.encode("")
    # Experience embedding
    if resume_like.get('experience'):
        experience_text = ""
        for exp in resume_like['experience']:
            exp_text = f"{exp.get('title', '')}"
            experience_text += exp_text + " "
        embeddings['experience'] = model.encode(experience_text.strip())
    else:
        embeddings['experience'] = model.encode("")
    # Education embedding
    if resume_like.get('education'):
        education_text = ""
        for edu in resume_like['education']:
            edu_text = f"{edu.get('degree', '')}"
            education_text += edu_text + " "
        embeddings['education'] = model.encode(education_text.strip())
    else:
        embeddings['education'] = model.encode("")
    # Job titles embedding
    job_titles_text = ""
    if resume_like.get('current_job_title'):
        job_titles_text += resume_like['current_job_title'] + " "
    if resume_like.get('preferred_job_title'):
        job_titles_text += resume_like['preferred_job_title'] + " "
    embeddings['job_titles'] = model.encode(job_titles_text.strip())
    return embeddings

def parse_embedding(emb_blob):
    """Convert BLOB back to numpy array"""
    if emb_blob is None:
        return np.zeros(384, dtype=np.float32)
    return np.frombuffer(emb_blob, dtype=np.float32)

def find_matching_resumes_by_similarity(jd_text, conn, top_n=10):
    """
    Find matching resumes using in-memory cosine similarity on SQLite data.
    """
    # 1. Generate Embeddings for the JD
    jd_embeddings = create_jd_section_embeddings(jd_text)
    
    # 2. Fetch all resumes from SQLite
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, location, current_job_title, preferred_job_title, 
               skills, experience, education,
               skills_embedding, experience_embedding, education_embedding, job_titles_embedding
        FROM resumes
    """)
    rows = cur.fetchall()
    
    if not rows:
        return []
        
    scored_resumes = []
    
    for row in rows:
        # Unpack row
        r_id, name, location, cur_title, pref_title, skills_json, exp_json, edu_json, skills_blob, exp_blob, edu_blob, titles_blob = row

        # Deserialize JSON fields
        try:
            skills = json.loads(skills_json) if skills_json else []
            experience = json.loads(exp_json) if exp_json else []
            education = json.loads(edu_json) if edu_json else []
        except json.JSONDecodeError:
            skills, experience, education = [], [], []

        # Parse Embeddings
        resume_embeddings = {
            'skills': parse_embedding(skills_blob),
            'experience': parse_embedding(exp_blob),
            'education': parse_embedding(edu_blob),
            'job_titles': parse_embedding(titles_blob)
        }
        
        # Calculate Similarity
        score = calculate_weighted_similarity(jd_embeddings, resume_embeddings)
        
        scored_resumes.append({
            "id": r_id,
            "name": name,
            "location": location,
            "current_job_title": cur_title,
            "skills": skills,
            "experience": experience,
            "education": education,
            "similarity_score": float(score)
        })
        
    # 3. Sort by score descending
    scored_resumes.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return scored_resumes[:top_n]
