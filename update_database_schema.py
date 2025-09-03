import os
from utils.db import create_updated_table, get_db_connection
from utils.extract_text import extract_text
from utils.clean_text import clean_text
from utils.groq_extractor import extract_structured_info_groq
import psycopg2
import json

def update_existing_resumes():
    """Update existing resumes in database with section-wise embeddings"""
    conn = get_db_connection()
    
    # Get all resumes that don't have section-wise embeddings
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, current_job_title, preferred_job_title, skills, experience, education
            FROM resumes 
            WHERE skills_embedding IS NULL OR experience_embedding IS NULL OR 
                  education_embedding IS NULL OR job_titles_embedding IS NULL
        """)
        resumes_to_update = cur.fetchall()
    
    print(f"Found {len(resumes_to_update)} resumes to update with section-wise embeddings")
    
    for resume_id, name, current_job_title, preferred_job_title, skills, experience, education in resumes_to_update:
        print(f"Processing resume: {name}")
        
        try:
            # Create section-wise embeddings
            embeddings = {}
            
            # Skills embedding
            if skills:
                skills_text = ", ".join(skills)
                embeddings['skills'] = model.encode(skills_text).tolist()
            else:
                embeddings['skills'] = model.encode("").tolist()
            
            # Experience embedding
            if experience:
                experience_data = json.loads(experience)
                experience_text = ""
                for exp in experience_data:
                    exp_text = f"{exp.get('title', '')} at {exp.get('company', '')} - {exp.get('description', '')}"
                    experience_text += exp_text + " "
                embeddings['experience'] = model.encode(experience_text.strip()).tolist()
            else:
                embeddings['experience'] = model.encode("").tolist()
            
            # Education embedding
            if education:
                education_data = json.loads(education)
                education_text = ""
                for edu in education_data:
                    edu_text = f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
                    education_text += edu_text + " "
                embeddings['education'] = model.encode(education_text.strip()).tolist()
            else:
                embeddings['education'] = model.encode("").tolist()
            
            # Job titles embedding
            job_titles_text = ""
            if current_job_title:
                job_titles_text += current_job_title + " "
            if preferred_job_title:
                job_titles_text += preferred_job_title + " "
            embeddings['job_titles'] = model.encode(job_titles_text.strip()).tolist()
            
            # Update the resume with embeddings
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE resumes 
                    SET skills_embedding = %s, experience_embedding = %s, 
                        education_embedding = %s, job_titles_embedding = %s
                    WHERE id = %s
                """, (
                    embeddings['skills'],
                    embeddings['experience'],
                    embeddings['education'],
                    embeddings['job_titles'],
                    resume_id
                ))
            
            print(f"✓ Updated {name} with section-wise embeddings")
            
        except Exception as e:
            print(f"✗ Error processing {name}: {str(e)}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Updating database schema...")
    create_updated_table()
    
    print("\nUpdating existing resumes with experience/education data...")
    update_existing_resumes()
    
    print("\nDatabase update complete!") 