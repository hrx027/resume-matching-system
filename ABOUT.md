# About the Project: Architecture & Technical Deep Dive

This document provides an in-depth technical explanation of the Resume Matching System, covering its dependencies, frontend implementation, and backend architecture.

---

## 1. Technical Stack & Dependencies

The project relies on a carefully selected set of Python libraries to handle everything from UI rendering to advanced AI processing.

### **Core Frameworks**
*   **`streamlit`**: The backbone of the application's Frontend. It converts Python scripts into a reactive web application, handling the UI rendering, event loop, and widget state management without requiring HTML/CSS/JavaScript knowledge.
*   **`pandas`**: Used for data structuring and manipulation. While the core logic uses JSON and lists, Pandas provides the underlying data structures for efficient data handling if we need to visualize or export results.

### **AI & Machine Learning**
*   **`sentence-transformers`**: This is the "Brain" of the semantic search engine.
    *   **Model Used**: `all-MiniLM-L6-v2`
    *   **Function**: It takes text (e.g., "Python Developer with AWS experience") and converts it into a 384-dimensional numerical vector (embedding). These vectors allow the system to understand the *meaning* of words rather than just matching keywords.
*   **`scikit-learn`**: Provides the mathematical engine for comparison.
    *   **Function**: specifically `cosine_similarity`. It calculates the angle between the Job Description vector and Resume vectors. A smaller angle means higher similarity (better match).

### **Data Processing & Extraction**
*   **`pdfplumber`**: A high-fidelity PDF extraction library.
    *   **Why**: Unlike older libraries, it accurately handles multi-column layouts commonly found in resumes, ensuring text is read in the correct reading order.
*   **`python-docx`**: Handles Microsoft Word (`.docx`) files, extracting raw text from paragraphs and tables.
*   **`requests`**: Manages HTTP communication with the Groq API. It sends the extracted raw text to the LLM for structuring.

### **Utilities**
*   **`python-dotenv`**: Security utility. It loads sensitive environment variables (like `GROQ_API_KEY`) from a local `.env` file, keeping secrets out of the codebase.
*   **`watchdog`**: A development utility used by Streamlit to monitor file changes and auto-reload the application during development.

---

## 2. Frontend Architecture (Streamlit)

The frontend is designed to be modern, responsive, and user-friendly, abstracting away the complex AI operations.

### **Structure & Layout**
*   **Sidebar Navigation**: Organized logically for workflow:
    1.  **Upload Section** (Top): Immediate access to data ingestion.
    2.  **Settings** (Middle): Fine-tuning controls (e.g., number of matches).
    3.  **Theme Toggle** (Bottom): User preference controls.
*   **Responsive Grid**: The main content area uses `st.columns([2, 1])` to give the Job Description (input) twice the width of the Action Controls, optimizing screen real estate.

### **State Management (`st.session_state`)**
Streamlit re-runs the entire script on every interaction. To prevent data loss, we use Session State:
*   **`db_ready`**: A flag to ensure the ephemeral database is initialized only once per session, not on every click.
*   **`theme`**: Persists the user's Dark/Light mode preference across re-runs.

### **Custom Styling (CSS Injection)**
We inject raw CSS via `st.markdown` to achieve a professional look that standard Streamlit doesn't offer:
*   **Card Design**: Custom HTML/CSS for result cards with hover effects (`transform: translateY`).
*   **Badges**: Styled pills for Skills and Roles.
*   **Icons**: Integration of FontAwesome libraries for professional iconography.

---

## 3. Backend Architecture (Logic & Data)

The backend follows a **Serverless, Ephemeral Architecture**. It requires no external database server (like Postgres or MySQL) and leaves no trace after execution.

### **A. The Data Pipeline**
*   **Ingestion**: Files are read and text is extracted using specialized libraries.
*   **Structuring**: The unstructured text is sent to an LLM to be converted into structured JSON.
*   **Vectorization**: The structured data is converted into numerical vectors (embeddings).
*   **Storage**: Data is stored in a temporary, in-memory (or temp-file) SQLite database.

### **B. Storage Layer (Ephemeral SQLite)**
*   **Technology**: SQLite (in-process database).
*   **Ephemeral Nature**: The database file is created in the system's temporary directory (`/tmp` or equivalent).
*   **Auto-Cleanup**: An `atexit` handler ensures the database file is physically deleted when the application process terminates.

### **C. The Matching Engine (`matching.py`)**
1.  **Query Processing**: The Job Description is processed through the same pipeline.
2.  **Multi-Dimensional Comparison**: We calculate four separate similarity scores (Skills, Experience, Education, Title).
3.  **Weighted Aggregation**:
    ```python
    Final Score = (Skills × 0.25) + (Experience × 0.25) + (Education × 0.15) + (Job Title × 0.35)
    ```

---

## 4. Data Flow & Resume Parsing Pipeline

This section details exactly how a resume file is transformed from a raw document into searchable data.

### **Step 1: File Ingestion**
*   **Trigger**: User drags and drops a file (PDF/DOCX) into the Streamlit interface.
*   **Action**: `app.py` saves the file to a temporary directory.
*   **Handler**: `resume_parser.process_all_resumes()` is called.

### **Step 2: Text Extraction**
*   **Module**: `extract_text.py`
*   **Logic**:
    *   **PDFs**: Uses `pdfplumber` to open the file and iterate through pages, extracting text while maintaining layout flow.
    *   **DOCX**: Uses `python-docx` to read paragraph elements.
*   **Output**: A single string of raw, often messy text.

### **Step 3: Text Cleaning**
*   **Module**: `clean_text.py`
*   **Action**: Removes special characters, excessive newlines, and non-printable characters to ensure the LLM receives clean input.

### **Step 4: AI Structuring (The "Parsing" Core)**
*   **Module**: `groq_extractor.py`
*   **Process**:
    1.  Constructs a prompt: *"You are an expert resume parser. Extract fields... Return JSON."*
    2.  Sends the request to **Groq API** (Llama 3 model).
    3.  Receives a structured JSON object containing:
        *   `name`: "John Doe"
        *   `skills`: ["Python", "AWS", "Docker"]
        *   `experience`: [{ "title": "Dev", "company": "A", "description": "..." }]
        *   `education`: [{ "degree": "BS", "institution": "B" }]

### **Step 5: Vectorization (Embedding)**
*   **Module**: `db.py`
*   **Process**:
    *   The system takes the text from specific sections (e.g., the list of skills).
    *   It passes this text to the `sentence-transformers` model.
    *   **Result**: A 384-dimensional vector (e.g., `[0.12, -0.45, 0.88, ...]`) representing the *semantic meaning* of those skills.
    *   This is done separately for Skills, Experience, Education, and Job Titles.

### **Step 6: Storage**
*   **Module**: `db.py` -> `insert_resume_into_db`
*   **Action**: The structured JSON and the generated vectors are inserted into the ephemeral SQLite database tables for fast retrieval during matching.
