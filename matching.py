import psycopg2
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.groq_extractor import extract_structured_info_groq_jd
import ast

DB_CONFIG = {
    "dbname": "resumes_db",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": 5433
}

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

def parse_embedding(emb):
    if emb is None:
        return np.array([])
    if isinstance(emb, list) or isinstance(emb, np.ndarray):
        return np.array(emb)
    if isinstance(emb, str):
        try:
            return np.array(ast.literal_eval(emb))
        except Exception:
            return np.array([])
    return np.array([])

def find_matching_resumes_by_similarity(jd_text, top_n=10):
    """Find matching resumes based purely on weighted cosine similarities"""
    jd_embeddings = create_jd_section_embeddings(jd_text)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get all resumes with their section-wise embeddings
    cur.execute("""
        SELECT id, name, current_job_title, preferred_job_title, skills, 
               experience, education, location, skills_embedding, experience_embedding,
               education_embedding, job_titles_embedding
        FROM resumes
    """)

    results = cur.fetchall()
    conn.close()

    if not results:
        print("No matches found for your filters.")
        return

    # Calculate weighted similarities for each resume using stored embeddings
    resume_scores = []
    
    for row in results:
        resume_id, name, current_job_title, preferred_job_title, skills, experience, education, location, skills_emb, experience_emb, education_emb, job_titles_emb = row
        
        # Use stored embeddings instead of computing them
        resume_embeddings = {
            'skills': parse_embedding(skills_emb),
            'experience': parse_embedding(experience_emb),
            'education': parse_embedding(education_emb),
            'job_titles': parse_embedding(job_titles_emb)
        }
        
        # Calculate weighted similarity
        weighted_similarity = calculate_weighted_similarity(jd_embeddings, resume_embeddings)
        
        resume_scores.append({
            'id': resume_id,
            'name': name,
            'current_job_title': current_job_title,
            'preferred_job_title': preferred_job_title,
            'skills': skills,
            'experience': experience,
            'education': education,
            'location': location,
            'similarity_score': weighted_similarity
        })
    
    # Sort by similarity score (higher is better)
    resume_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Return top N results
    top_results = resume_scores[:top_n]
    
    for i, result in enumerate(top_results, start=1):
        print(f"\n🔹 Match #{i}")
        print(f"Name: {result['name']}")
        print(f"Current Title: {result['current_job_title']}")
        print(f"Preferred Title: {result['preferred_job_title']}")
        print(f"Location: {result['location']}")
        print(f"Skills: {result['skills']}")
        print(f"Weighted Similarity Score: {result['similarity_score']:.4f}")
        
        # Show section breakdown
        if result['experience']:
            print(f"Experience: {len(result['experience'])} positions")
        if result['education']:
            print(f"Education: {len(result['education'])} degrees")

