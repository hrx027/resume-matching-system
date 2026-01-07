# Deployment Guide for Resume Matching System

This guide covers how to deploy the Resume Matching System to **Streamlit Community Cloud** (recommended for ease) or a VPS/PaaS like **Render**.

## Prerequisites
1. A GitHub account.
2. A Groq API Key.

## Option 1: Streamlit Community Cloud (Easiest)

1. **Push your code to GitHub**
   - Create a new repository on GitHub.
   - Push all files in this folder to the repository.
   - Ensure `requirements.txt` is in the root.

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Sign in with GitHub.
   - Click "New app".
   - Select your repository, branch (usually `main`), and main file path (`app.py`).

3. **Configure Secrets (Environment Variables)**
   - Before clicking "Deploy", click "Advanced Settings".
   - Go to the "Secrets" section.
   -# Add your secrets in TOML format:
     ```toml
     GROQ_API_KEY = "your-groq-api-key-here"
      GROQ_MODEL = "llama-3.1-8b-instant"
      
      # Database credentials (e.g. from Neon.tech, Supabase, or Render)
    DB_NAME = "your-db-name"
    DB_USER = "your-db-user"
    DB_PASSWORD = "your-db-password"
    DB_HOST = "your-db-host"
    DB_PORT = "5432"
    
    # Hugging Face Model Setting
    HF_HUB_OFFLINE = "0" 
    # Set to "0" to download models on the server. "1" only works if models are pre-cached/uploaded.
     ```
   *Note: The current app uses a local PostgreSQL database. For deployment, you need a cloud PostgreSQL instance (e.g., from Neon.tech, Supabase, or Render).*

4. **Deploy**
   - Click "Deploy". Streamlit will install dependencies from `requirements.txt` and start the app.

## Option 2: Render.com (For Full Stack Control)

1. **Create a PostgreSQL Database on Render**
   - Go to Dashboard > New > PostgreSQL.
   - Copy the `Internal Database URL`.

2. **Create a Web Service**
   - Go to Dashboard > New > Web Service.
   - Connect your GitHub repo.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT`

3. **Environment Variables**
   - Add the following env vars:
     - `PYTHON_VERSION`: `3.9` (or match your local version)
     - `HF_HUB_OFFLINE`: `0`
     - `DB_HOST`, `DB_USER`, etc. (Use the details from the Postgres DB you created).

## Important Note on Database
The code currently defaults to `localhost`. You need to modify `db.py` to read from environment variables for production.

**Recommended change for `db.py`:**
```python
import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "resumes_db"),
    "user": os.getenv("DB_USER", "resume_user"),
    "password": os.getenv("DB_PASSWORD", "hrx1234"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
```
