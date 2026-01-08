# Resume Matching System

A comprehensive AI-powered resume matching system that automatically parses resumes, extracts structured information using Large Language Models (LLMs), and matches candidates to job descriptions using semantic similarity and weighted scoring algorithms.

## 🎯 Project Overview

This system addresses the critical challenge of efficiently matching job candidates to job descriptions in the recruitment process. It combines:

- **Document Processing**: Extracts text from PDF and DOCX resume files
- **AI-Powered Parsing**: Uses Groq's LLM API to extract structured information from unstructured resume text
- **Semantic Matching**: Employs sentence transformers and cosine similarity for intelligent candidate-job matching
- **Section-Wise Analysis**: Implements weighted scoring across multiple resume sections (skills, experience, education, job titles)
- **Database Management**: Stores resumes in PostgreSQL with vector embeddings for efficient similarity search
- **Streamlit Frontend**: A modern web interface for uploading resumes and finding matches

## 🏗️ Architecture & Design Decisions

### Technology Stack

- **Language**: Python 3.x
- **Database**: PostgreSQL with pgvector extension for vector similarity search
- **LLM Integration**: Groq API (Llama3-8b-8192) for structured information extraction
- **Embeddings**: SentenceTransformer (`all-MiniLM-L6-v2`) for generating 384-dimensional embeddings
- **Text Processing**: `pdfplumber` for PDF extraction, `python-docx` for DOCX files
- **Similarity Calculation**: Scikit-learn's cosine similarity with custom weighted scoring
- **Frontend**: Streamlit

### Key Design Decisions

1. **Section-Wise Embeddings**: Instead of creating a single embedding for the entire resume, the system generates separate embeddings for:
   - Skills
   - Experience
   - Education
   - Job Titles
   
   This approach allows for more granular matching and enables weighted scoring based on the importance of different sections.

2. **Weighted Similarity Scoring**: Different resume sections are weighted differently:
   - Job Titles: 35% (highest weight - most indicative of fit)
   - Skills: 25%
   - Experience: 25%
   - Education: 15% (lowest weight)

3. **LLM-Based Extraction**: Uses Groq's LLM API instead of traditional regex/NLP parsing, enabling:
   - Better handling of varied resume formats
   - More accurate extraction of structured data
   - Natural language understanding for ambiguous fields

4. **Duplicate Prevention**: Implements MD5 hashing of resume content to prevent duplicate entries in the database.

## 📁 Project Structure

```
resume-matching-system/
├── clean_text.py              # Text preprocessing utilities
├── db.py                      # Database operations and schema management
├── extract_text.py            # PDF/DOCX text extraction
├── generate_resumes.py        # Sample resume generation for testing
├── groq_extractor.py          # LLM-based structured information extraction
├── match_resumes.py           # Main script for finding matching resumes
├── matching.py                # Core matching algorithm with weighted similarity
├── resume_parser.py           # Batch resume processing pipeline
├── update_database_schema.py  # Database migration and schema updates
├── app.py                     # Streamlit web application
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── DEPLOYMENT.md              # Deployment guide
```

## 🚀 Installation & Setup

### Prerequisites

1. **Python 3.9+**
2. **PostgreSQL** with `pgvector` extension installed
3. **Groq API Key** (Sign up at https://groq.com)

### Step 1: Clone the Repository

```bash
git clone https://github.com/hrx027/resume-matching-system.git
cd resume-matching-system
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory and add your configuration:

```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
DB_NAME=resumes_db
DB_USER=resume_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 5: Setup Database

Ensure PostgreSQL is running and your user has permissions to create databases.

```bash
# Initialize the database schema (Not needed for ephemeral mode, but good to check connection)
# python resume_parser.py
```

## 💻 Usage

### Option 1: Run the Web App (Recommended)

Start the Streamlit interface to upload resumes and match them interactively.

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Option 2: CLI Batch Processing

**1. Process Resumes from Folder:**
Place your resume files (PDF or DOCX) in a `./resumes` folder, then run:

```bash
python resume_parser.py
```
This will extract text, parse information using LLM, generate embeddings, and store them in the database.

**2. Find Matching Candidates:**
Run the matching script to find best candidates for a job description.

```bash
python match_resumes.py
```

## 🧪 Testing

The project includes `generate_resumes.py` which creates 5 sample resumes for testing:
- Ishaan Tyagi (Backend Engineer)
- Meenakshi Patel (Data Analyst)
- Tanmay Kulkarni (MLOps Engineer)
- Shivangi Rana (Data Science fresher)
- Devansh Bhatt (Backend Developer)

To generate them:
```bash
python generate_resumes.py
```

## 🔍 Algorithm Details

### Embedding Generation
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Fast inference, good quality for semantic similarity
- Each section embedded separately for granular matching

### Similarity Calculation
```python
weighted_score = (
    skills_similarity * 0.25 +
    experience_similarity * 0.25 +
    education_similarity * 0.15 +
    job_titles_similarity * 0.35
)
```

## 🤝 Contributing

This project demonstrates:
- End-to-end ML pipeline development
- Integration of LLMs into production systems
- Database design for vector similarity search
- Clean, modular code architecture
- Error handling and data validation

---

**Built for**: Efficient candidate-job matching in recruitment workflows  
**Technologies**: Python, PostgreSQL, LLMs, Sentence Transformers, Vector Similarity Search, Streamlit
