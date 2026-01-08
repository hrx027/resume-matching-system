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
     
     # Cloud PostgreSQL Connection String (e.g. from Supabase, Neon, Render)
     # Ensure you use the 'Transaction' pooler URL if using Supabase (port 6543) or Session pooler (port 5432)
     # Must start with postgres:// or postgresql://
     DATABASE_URL = "postgresql://user:password@host:port/dbname?sslmode=require"
     
     # Hugging Face Model Setting
     HF_HUB_OFFLINE = "0" 
     ```
     *Note: You need a cloud PostgreSQL instance (e.g., from Neon.tech, Supabase, or Render).*

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
     - `DATABASE_URL`: Your full PostgreSQL connection string (e.g. `postgresql://user:pass@host:port/dbname`)

## Important Note on Database
The code now uses `DATABASE_URL` for connection. You must provide this environment variable.

**`db.py` uses:**
```python
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except:
        pass
```
