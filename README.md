# Resume Matching System

A Streamlit app that parses multiple resumes, extracts structured data using Groq LLMs, and ranks candidates against a job description using section-wise embeddings and weighted cosine similarity.

## 🎯 Project Overview

This system addresses the critical challenge of efficiently matching job candidates to job descriptions in the recruitment process. It combines:

- **Document Processing**: Extracts text from PDF and DOCX resume files
- **AI-Powered Parsing**: Uses Groq's LLM API to extract structured information from unstructured resume text
- **Semantic Matching**: Employs Sentence Transformers and cosine similarity for intelligent candidate-job matching
- **Section-Wise Analysis**: Implements weighted scoring across multiple resume sections (skills, experience, education, job titles)
- **Ephemeral Storage**: Stores resumes in a temporary SQLite database that is deleted when the app stops
- **Streamlit Frontend**: A modern web interface for uploading resumes and finding matches

## 🏗️ Architecture & Design Decisions

### Technology Stack

- **Language**: Python 3.x
- **Database**: SQLite (temporary file in system temp directory)
- **LLM Integration**: Groq API for structured information extraction
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

4. **Ephemeral By Default**: Resume data exists only while the app is running. When Streamlit stops/restarts, the temporary DB is removed.

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
├── app.py                     # Streamlit web application
├── requirements.txt           # Python dependencies
├── .env                       # Local-only environment variables (not committed)
└── DEPLOYMENT.md              # Deployment guide
```

## 🚀 Installation & Setup

### Prerequisites

1. **Python 3.9+**
2. **Groq API Key** (Sign up at https://groq.com)

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

Create a `.env` file in the root directory and add your configuration (this file is ignored by git):

```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

No external database setup is required. The app uses a temporary SQLite database that is created automatically.

## 💻 Usage

### Run the Web App (Recommended)

Start the Streamlit interface to upload resumes and match them interactively.

```bash
python3 -m streamlit run app.py
```
Open your browser at `http://localhost:8501` (or the next available port if 8501 is in use).

## 🔒 Data & Privacy

- Resume data is stored only while the app is running.
- When the Streamlit process stops/restarts, the temporary database file is deleted.
- Do not commit `.env` to git. Add secrets in Streamlit Cloud “Secrets” when deploying.

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
**Technologies**: Python, SQLite (ephemeral), Groq LLMs, Sentence Transformers, Cosine Similarity, Streamlit
