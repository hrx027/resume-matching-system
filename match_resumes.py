from matching import find_matching_resumes_by_similarity
from db import create_updated_table
from resume_parser import process_all_resumes

if __name__ == "__main__":
    # Initialize ephemeral DB and populate with resumes
    print("Initializing ephemeral database...")
    conn = create_updated_table()
    
    print("Populating resumes...")
    process_all_resumes(conn)
    
    jd = """
    Job Description: Machine Learning Engineer (NLP Focus)
    Position: Machine Learning Engineer
    Location: Bangalore, India (Hybrid)
    Experience Required: 2-5 years
    Company: LexiAI Technologies Pvt. Ltd.

    About the Role:
    We’re seeking a highly skilled Machine Learning Engineer with a focus on Natural Language Processing to join our AI team. You will work on building and optimizing large language models, transformers, and intelligent data pipelines that process and analyze unstructured textual data from millions of customer documents.

    Responsibilities:
    Develop NLP pipelines for text classification, named entity recognition (NER), topic modeling, and summarization.
    Optimize transformer-based models (BERT, RoBERTa, SBERT, etc.) for production.
    Collaborate with product and backend teams to integrate ML models into APIs.
    Maintain clean, modular code using best practices in Python.
    Perform model evaluation, tuning, and deployment using MLOps practices.
    Document and present model performance clearly to non-technical stakeholders.

    Requirements:
    Bachelor’s/Master’s degree in Computer Science, Data Science, or related field.
    2+ years of experience in ML/NLP.
    Strong hands-on experience with Python, Scikit-learn, PyTorch or TensorFlow.
    Experience with Hugging Face Transformers.
    Proficiency in NLP libraries (spaCy, NLTK, Gensim).
    Familiarity with RESTful APIs, Docker, and Git.

    Bonus: Experience with cloud services (AWS/GCP), FastAPI, or vector databases (e.g., Pinecone, pgvector).
    """
    
    print("\nRunning search...")
    find_matching_resumes_by_similarity(
        jd_text=jd,
        conn=conn,
        top_n=3
    )
    conn.close()
