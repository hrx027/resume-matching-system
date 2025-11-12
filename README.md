# Resume Matching System

A comprehensive AI-powered resume matching system that automatically parses resumes, extracts structured information using Large Language Models (LLMs), and matches candidates to job descriptions using semantic similarity and weighted scoring algorithms.

## 🎯 Project Overview

This system addresses the critical challenge of efficiently matching job candidates to job descriptions in the recruitment process. It combines:

- **Document Processing**: Extracts text from PDF and DOCX resume files
- **AI-Powered Parsing**: Uses Groq's LLM API to extract structured information from unstructured resume text
- **Semantic Matching**: Employs sentence transformers and cosine similarity for intelligent candidate-job matching
- **Section-Wise Analysis**: Implements weighted scoring across multiple resume sections (skills, experience, education, job titles)
- **Database Management**: Stores resumes in PostgreSQL with vector embeddings for efficient similarity search

## 🏗️ Architecture & Design Decisions

### Technology Stack

- **Language**: Python 3.x
- **Database**: PostgreSQL with pgvector extension for vector similarity search
- **LLM Integration**: Groq API (Llama3-8b-8192) for structured information extraction
- **Embeddings**: SentenceTransformer (`all-MiniLM-L6-v2`) for generating 384-dimensional embeddings
- **Text Processing**: `pdfplumber` for PDF extraction, `python-docx` for DOCX files
- **Similarity Calculation**: Scikit-learn's cosine similarity with custom weighted scoring

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
└── update_database_schema.py  # Database migration and schema updates
```

## 🔧 Core Components

### 1. Text Extraction (`extract_text.py`)
- Supports PDF and DOCX file formats
- Handles multi-page documents
- Returns clean text for further processing

### 2. Text Cleaning (`clean_text.py`)
- Normalizes text to lowercase
- Removes extra whitespace
- Strips punctuation for consistent processing
- Prepares text for LLM extraction

### 3. LLM-Based Extraction (`groq_extractor.py`)
- **`extract_structured_info_groq()`**: Extracts structured data from resumes
  - Name, location, job titles
  - Skills (as array)
  - Experience (company, title, duration, description)
  - Education (institution, degree, field, year)
  
- **`extract_structured_info_groq_jd()`**: Extracts structured data from job descriptions
  - Job title, required skills, experience, education, location

### 4. Database Management (`db.py`)
- **Schema**: PostgreSQL table with columns for:
  - Basic info: `name`, `location`, `current_job_title`, `preferred_job_title`
  - Structured data: `skills` (array), `experience` (JSONB), `education` (JSONB)
  - Embeddings: `skills_embedding`, `experience_embedding`, `education_embedding`, `job_titles_embedding` (vector(384))
  - Deduplication: `resume_hash` (MD5)
  
- **Embedding Generation**: Creates section-wise embeddings using SentenceTransformer
- **Duplicate Detection**: Uses content hashing to prevent duplicate resume entries

### 5. Matching Algorithm (`matching.py`)
- **Weighted Cosine Similarity**: Calculates similarity scores across multiple sections
- **Section-Wise Comparison**: Compares job description requirements with candidate resume sections
- **Top-N Results**: Returns ranked list of best-matching candidates

### 6. Resume Processing Pipeline (`resume_parser.py`)
- Batch processes all resumes in a specified folder
- Extracts text → Cleans text → Extracts structured info → Inserts into database
- Handles errors gracefully and skips duplicates

## 🚀 Usage

### Prerequisites

1. **PostgreSQL Setup**:
   ```bash
   # Install PostgreSQL with pgvector extension
   # Update DB_CONFIG in db.py with your credentials
   ```

2. **Python Dependencies**:
   ```bash
   pip install psycopg2-binary sentence-transformers pdfplumber python-docx fpdf scikit-learn requests
   ```

3. **Groq API Key**:
   - Sign up at https://groq.com
   - Add your API key to `groq_extractor.py` (line 6)

### Step 1: Initialize Database Schema

```bash
python update_database_schema.py
```

This creates the necessary tables and columns with vector support.

### Step 2: Process Resumes

Place your resume files (PDF or DOCX) in a `./resumes` folder, then run:

```bash
python resume_parser.py
```

This will:
- Extract text from all resumes
- Use Groq LLM to extract structured information
- Generate section-wise embeddings
- Insert into database (skipping duplicates)

### Step 3: Find Matching Candidates

```bash
python match_resumes.py
```

Or programmatically:

```python
from utils.matching import find_matching_resumes_by_similarity

jd_text = """
Job Description: Machine Learning Engineer
Requirements: Python, TensorFlow, 3+ years experience
...
"""

find_matching_resumes_by_similarity(jd_text=jd_text, top_n=5)
```

## 🧪 Testing

The project includes `generate_resumes.py` which creates 5 sample resumes for testing:
- Ishaan Tyagi (Backend Engineer)
- Meenakshi Patel (Data Analyst)
- Tanmay Kulkarni (MLOps Engineer)
- Shivangi Rana (Data Science fresher)
- Devansh Bhatt (Backend Developer)

## 💡 Key Features & Highlights

### 1. **Intelligent Parsing**
- Handles varied resume formats without rigid templates
- LLM understands context and extracts relevant information even from unstructured text

### 2. **Semantic Matching**
- Goes beyond keyword matching
- Understands semantic relationships (e.g., "ML Engineer" matches "Machine Learning Engineer")
- Uses state-of-the-art sentence transformers

### 3. **Weighted Scoring**
- Configurable weights allow prioritizing different aspects
- Job titles weighted highest (35%) as they're most indicative of fit
- Flexible system that can be tuned for different use cases

### 4. **Scalability**
- Pre-computed embeddings stored in database
- Efficient similarity search using vector operations
- Batch processing support for large volumes of resumes

### 5. **Robustness**
- Duplicate detection prevents data redundancy
- Error handling for malformed resumes
- Graceful degradation when sections are missing

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

### Matching Process
1. Extract structured info from job description using LLM
2. Generate section-wise embeddings for JD
3. Retrieve all resumes with pre-computed embeddings
4. Calculate weighted cosine similarity for each resume
5. Rank and return top N matches

## 🎓 Interview Talking Points

### Technical Challenges Solved

1. **Handling Unstructured Data**: Resumes come in various formats. The LLM-based approach handles this variability better than regex-based parsers.

2. **Semantic Understanding**: Traditional keyword matching fails when terms differ but meanings align. Sentence transformers capture semantic relationships.

3. **Balanced Scoring**: Determining optimal weights required understanding recruitment priorities. Job titles are weighted highest as they're most predictive of fit.

4. **Performance Optimization**: Pre-computing embeddings avoids recalculating for every query, enabling fast similarity search.

5. **Data Quality**: MD5 hashing prevents duplicate entries, maintaining database integrity.

### Scalability Considerations

- **Database Indexing**: Vector columns can be indexed for faster similarity search
- **Batch Processing**: Resume processing pipeline handles large volumes efficiently
- **API Rate Limiting**: Groq API calls include rate limiting considerations (sleep delays)

### Future Enhancements

- **Real-time Updates**: Webhook-based resume ingestion
- **Fine-tuning**: Custom embedding models trained on resume data
- **Explainability**: Detailed breakdown of why candidates match
- **Multi-language Support**: Extend to handle resumes in different languages
- **Advanced Filtering**: Location, salary range, availability filters

## 📊 Database Schema

```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location TEXT,
    current_job_title TEXT,
    preferred_job_title TEXT,
    skills TEXT[],
    experience JSONB,
    education JSONB,
    resume_hash TEXT UNIQUE,
    skills_embedding vector(384),
    experience_embedding vector(384),
    education_embedding vector(384),
    job_titles_embedding vector(384)
);
```

## 🔐 Configuration

Key configuration files:
- **`db.py`**: Database connection settings
- **`groq_extractor.py`**: Groq API key and model selection
- **`matching.py`**: Section weights for scoring algorithm

## 📝 Notes

- The system requires PostgreSQL with the `pgvector` extension for vector operations
- Groq API has rate limits; the code includes appropriate delays
- Resume folder path is configurable in `resume_parser.py`
- All embeddings use 384-dimensional vectors (compatible with `all-MiniLM-L6-v2`)

## 🤝 Contributing

This project demonstrates:
- End-to-end ML pipeline development
- Integration of LLMs into production systems
- Database design for vector similarity search
- Clean, modular code architecture
- Error handling and data validation

---

**Built for**: Efficient candidate-job matching in recruitment workflows  
**Technologies**: Python, PostgreSQL, LLMs, Sentence Transformers, Vector Similarity Search

