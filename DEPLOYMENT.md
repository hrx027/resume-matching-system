# Deployment Guide for Resume Matching System

This guide covers how to deploy the Resume Matching System to **Streamlit Community Cloud** (recommended for ease).

## Prerequisites
1. A GitHub account.
2. A Groq API Key.

## Streamlit Community Cloud (Easiest)

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
   - Add your secrets in TOML format:
     ```toml
     GROQ_API_KEY = "your-groq-api-key-here"
     GROQ_MODEL = "openai/gpt-oss-120b"  # or your preferred model
     ```
   - **No Database URL is needed!** The app now uses an internal, ephemeral database that runs automatically.

4. **Deploy**
   - Click "Deploy". Streamlit will install dependencies from `requirements.txt` and start the app.

## How it Works
The application now uses **SQLite in memory/temp file mode**.
- **Ephemeral**: The database is created in the system's temporary folder when the app starts.
- **Privacy**: When the app stops or restarts, the database is automatically deleted. No resume data is permanently stored.
- **Zero Config**: No external database setup (Supabase, Neon, etc.) is required.
