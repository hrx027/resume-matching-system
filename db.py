import psycopg2
import json
import hashlib
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except (ImportError, FileNotFoundError):
        pass

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db_connection():
    if "DATABASE_URL" not in os.environ:
        raise RuntimeError("DATABASE_URL not found in environment variables.")
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

def create_updated_table():
    """Create a temporary resumes table with section-wise embeddings"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Enable vector extension (requires superuser or db owner privileges usually)
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Create temporary table that persists for the session (connection)
        cur.execute("""
        CREATE TEMP TABLE IF NOT EXISTS resumes (
            id SERIAL,
            name TEXT,
            location TEXT,
            current_job_title TEXT,
            preferred_job_title TEXT,
            skills TEXT[],
            experience JSONB,
            education JSONB,
            resume_hash TEXT,
            skills_embedding vector(384),
            experience_embedding vector(384),
            education_embedding vector(384),
            job_titles_embedding vector(384)
        ) ON COMMIT PRESERVE ROWS;
        """)
    conn.commit()
    # Return the connection so it can be kept open to maintain the TEMP table
    return conn

def insert_resume_into_db(conn, structured_info):
    # Create a unique hash for the resume based on its content
    resume_content = json.dumps(structured_info, sort_keys=True)
    resume_hash = hashlib.md5(resume_content.encode()).hexdigest()
    
    # Removed duplicate checking logic as requested for ephemeral session storage
    
    # Create section-wise embeddings from structured info
    embeddings = {}
    
    # Skills embedding
    if structured_info.get("skills"):
        skills_text = ", ".join(structured_info["skills"])
        embeddings['skills'] = model.encode(skills_text).tolist()
    else:
        embeddings['skills'] = model.encode("").tolist()
    
    # Experience embedding
    if structured_info.get("experience"):
        experience_text = ""
        for exp in structured_info["experience"]:
            exp_text = f"{exp.get('title', '')} at {exp.get('company', '')} - {exp.get('description', '')}"
            experience_text += exp_text + " "
        embeddings['experience'] = model.encode(experience_text.strip()).tolist()
    else:
        embeddings['experience'] = model.encode("").tolist()
    
    # Education embedding
    if structured_info.get("education"):
        education_text = ""
        for edu in structured_info["education"]:
            edu_text = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
            education_text += edu_text + " "
        embeddings['education'] = model.encode(education_text.strip()).tolist()
    else:
        embeddings['education'] = model.encode("").tolist()
    
    # Job titles embedding
    job_titles_text = ""
    if structured_info.get("current_job_title"):
        job_titles_text += structured_info["current_job_title"] + " "
    if structured_info.get("preferred_job_title"):
        job_titles_text += structured_info["preferred_job_title"] + " "
    embeddings['job_titles'] = model.encode(job_titles_text.strip()).tolist()

    with conn.cursor() as cur:
        skills_array = structured_info.get("skills") or []
        experience_data = json.dumps(structured_info.get("experience") or [])
        education_data = json.dumps(structured_info.get("education") or [])

        cur.execute("""
            INSERT INTO resumes (
                name, location, current_job_title, preferred_job_title, 
                skills, experience, education, resume_hash, skills_embedding, experience_embedding, 
                education_embedding, job_titles_embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            structured_info.get("name"),
            structured_info.get("location"),
            structured_info.get("current_job_title"),
            structured_info.get("preferred_job_title"),
            skills_array,
            experience_data,
            education_data,
            resume_hash,
            embeddings['skills'],
            embeddings['experience'],
            embeddings['education'],
            embeddings['job_titles']
        ))
    conn.commit()
    return True
