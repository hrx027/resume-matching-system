import psycopg2
import json
import hashlib
from sentence_transformers import SentenceTransformer

DB_CONFIG = {
    "dbname": "resumes_db",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": 5433
}

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_updated_table():
    """Create or update the resumes table with section-wise embeddings and remove old columns"""
    conn = get_db_connection()
    
    with conn.cursor() as cur:
        # Check if inline_resume column exists and remove it
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resumes' 
            AND column_name = 'inline_resume'
        """)
        if cur.fetchone():
            cur.execute("ALTER TABLE resumes DROP COLUMN inline_resume")
            print("✓ Removed inline_resume column")
        
        # Check if old embedding column exists and remove it
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resumes' 
            AND column_name = 'embedding'
        """)
        if cur.fetchone():
            cur.execute("ALTER TABLE resumes DROP COLUMN embedding")
            print("✓ Removed embedding column")
        
        # Check if resume_hash column exists, if not add it
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resumes' 
            AND column_name = 'resume_hash'
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE resumes ADD COLUMN resume_hash TEXT UNIQUE")
            print("✓ Added resume_hash column")
        
        # Check if experience and education columns exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resumes' 
            AND column_name IN ('experience', 'education')
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        # Add experience column if it doesn't exist
        if 'experience' not in existing_columns:
            cur.execute("ALTER TABLE resumes ADD COLUMN experience JSONB")
            print("✓ Added experience column")
        
        # Add education column if it doesn't exist
        if 'education' not in existing_columns:
            cur.execute("ALTER TABLE resumes ADD COLUMN education JSONB")
            print("✓ Added education column")
        
        # Add section-wise embedding columns
        embedding_columns = ['skills_embedding', 'experience_embedding', 'education_embedding', 'job_titles_embedding']
        for col in embedding_columns:
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'resumes' 
                AND column_name = '{col}'
            """)
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE resumes ADD COLUMN {col} vector(384)")
                print(f"✓ Added {col} column")
    
    conn.commit()
    conn.close()

def insert_resume_into_db(conn, structured_info):
    # Create a unique hash for the resume based on its content
    resume_content = json.dumps(structured_info, sort_keys=True)
    resume_hash = hashlib.md5(resume_content.encode()).hexdigest()
    
    # Check if resume already exists using the hash
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM resumes 
            WHERE resume_hash = %s
        """, (resume_hash,))
        
        existing_resume = cur.fetchone()
        if existing_resume:
            print(f"⚠️ Resume with hash {resume_hash[:8]}... already exists. Skipping.")
            return False
    
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
