import os
from extract_text import extract_text
from clean_text import clean_text
from groq_extractor import extract_structured_info_groq
from db import insert_resume_into_db, get_db_connection

RESUME_FOLDER = "./resumes"

def process_all_resumes(conn, resume_folder=RESUME_FOLDER):
    # conn is passed from the caller (app.py) which manages the session connection
    
    if not os.path.exists(resume_folder):
        print(f"Folder {resume_folder} does not exist.")
        return

    for file in os.listdir(resume_folder):
        path = os.path.join(resume_folder, file)
        if not os.path.isfile(path) or not file.lower().endswith(('.pdf', '.docx', '.doc')):
            continue

        print(f"Processing: {file}")
        raw_text = extract_text(path)
        cleaned_text = clean_text(raw_text)

        structured_info = extract_structured_info_groq(cleaned_text)
        if structured_info:
            success = insert_resume_into_db(conn, structured_info)
            if success:
                print(f"✓ Inserted {file}")
            # If success is False, the resume already exists and was skipped
        else:
            print(f"✗ Skipped {file} due to extraction failure.")

    # Connection is managed by the caller, do not close it here

if __name__ == "__main__":
    from db import create_updated_table
    # For standalone testing, create a temp connection
    conn = create_updated_table()
    process_all_resumes(conn)
    conn.close()
