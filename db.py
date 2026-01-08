import sqlite3
import json
import hashlib
import os
import tempfile
import atexit
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Temporary Database File
_temp_db_file = os.path.join(tempfile.gettempdir(), "runtime_resume_db.sqlite")

def get_db_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(_temp_db_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable accessing columns by name
    return conn

def init_db():
    """Initialize the database schema"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT,
        current_job_title TEXT,
        preferred_job_title TEXT,
        skills TEXT,          -- Stored as JSON string
        experience TEXT,      -- Stored as JSON string
        education TEXT,       -- Stored as JSON string
        resume_hash TEXT,
        skills_embedding BLOB,
        experience_embedding BLOB,
        education_embedding BLOB,
        job_titles_embedding BLOB
    )
    """)

    conn.commit()
    conn.close()

def cleanup():
    """Remove the temporary database file on exit"""
    if os.path.exists(_temp_db_file):
        try:
            os.remove(_temp_db_file)
        except OSError:
            pass

atexit.register(cleanup)

def insert_resume_into_db(conn, structured_info):
    # Create a unique hash for the resume based on its content
    resume_content = json.dumps(structured_info, sort_keys=True)
    resume_hash = hashlib.md5(resume_content.encode()).hexdigest()
    
    # Create section-wise embeddings from structured info
    embeddings = {}
    
    # Skills embedding
    if structured_info.get("skills"):
        skills_text = ", ".join(structured_info["skills"])
        embeddings['skills'] = model.encode(skills_text).astype(np.float32).tobytes()
    else:
        embeddings['skills'] = model.encode("").astype(np.float32).tobytes()
    
    # Experience embedding
    if structured_info.get("experience"):
        experience_text = ""
        for exp in structured_info["experience"]:
            exp_text = f"{exp.get('title', '')} at {exp.get('company', '')} - {exp.get('description', '')}"
            experience_text += exp_text + " "
        embeddings['experience'] = model.encode(experience_text.strip()).astype(np.float32).tobytes()
    else:
        embeddings['experience'] = model.encode("").astype(np.float32).tobytes()
    
    # Education embedding
    if structured_info.get("education"):
        education_text = ""
        for edu in structured_info["education"]:
            edu_text = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
            education_text += edu_text + " "
        embeddings['education'] = model.encode(education_text.strip()).astype(np.float32).tobytes()
    else:
        embeddings['education'] = model.encode("").astype(np.float32).tobytes()
    
    # Job titles embedding
    job_titles_text = ""
    if structured_info.get("current_job_title"):
        job_titles_text += structured_info["current_job_title"] + " "
    if structured_info.get("preferred_job_title"):
        job_titles_text += structured_info["preferred_job_title"] + " "
    embeddings['job_titles'] = model.encode(job_titles_text.strip()).astype(np.float32).tobytes()

    # Prepare data for insertion
    # Arrays/JSON objects must be serialized to strings for SQLite
    skills_json = json.dumps(structured_info.get("skills", []))
    experience_json = json.dumps(structured_info.get("experience", []))
    education_json = json.dumps(structured_info.get("education", []))

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes (
            name, location, current_job_title, preferred_job_title, 
            skills, experience, education, resume_hash,
            skills_embedding, experience_embedding, education_embedding, job_titles_embedding
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        structured_info.get("name"),
        structured_info.get("location"),
        structured_info.get("current_job_title"),
        structured_info.get("preferred_job_title"),
        skills_json,
        experience_json,
        education_json,
        resume_hash,
        embeddings['skills'],
        embeddings['experience'],
        embeddings['education'],
        embeddings['job_titles']
    ))
    conn.commit()
