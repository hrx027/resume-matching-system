import os
from utils.extract_text import extract_text
from utils.clean_text import clean_text
from utils.groq_extractor import extract_structured_info_groq
from utils.db import insert_resume_into_db, get_db_connection

RESUME_FOLDER = "./resumes"

def process_all_resumes():
    conn = get_db_connection()

    for file in os.listdir(RESUME_FOLDER):
        path = os.path.join(RESUME_FOLDER, file)
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

    conn.close()

if __name__ == "__main__":
    process_all_resumes()
