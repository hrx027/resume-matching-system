import requests
import json
import re
import time

GROQ_API_KEY = "yahan pe key daalni h"
GROQ_MODEL = "llama3-8b-8192"

PROMPT_TEMPLATE = """
You are an expert resume parser.

Extract the following fields from this resume:
- name
- location
- current job title
- preferred job title (if mentioned)
- skills (as a list)
- experience (list of work experience with company, title, duration, description)
- education (list of education with institution, degree, field, year)

Return the result as valid JSON in this format:
{{
  "name": "...",
  "location": "...",
  "current_job_title": "...",
  "preferred_job_title": "...",
  "skills": ["...", "..."],
  "experience": [
    {{
      "company": "...",
      "title": "...",
      "duration": "...",
      "description": "..."
    }}
  ],
  "education": [
    {{
      "institution": "...",
      "degree": "...",
      "field": "...",
      "year": "..."
    }}
  ]
}}

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

def extract_structured_info_groq(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = {
        "role": "system",
        "content": (
            "You're an AI that extracts structured info from resumes. "
            "Return ONLY a valid JSON object with the following fields:\n"
            "- name (string)\n"
            "- location (string)\n"
            "- current_job_title (string)\n"
            "- preferred_job_title (string)\n"
            "- skills (array of strings)\n"
            "- experience (array of objects with company, title, duration, description)\n"
            "- education (array of objects with institution, degree, field, year)\n\n"
            "Example:\n"
            "{\n"
            "  \"name\": \"John Doe\",\n"
            "  \"location\": \"New York, USA\",\n"
            "  \"current_job_title\": \"Software Engineer\",\n"
            "  \"preferred_job_title\": \"Senior ML Engineer\",\n"
            "  \"skills\": [\"Python\", \"Machine Learning\", \"TensorFlow\"],\n"
            "  \"experience\": [\n"
            "    {\n"
            "      \"company\": \"Tech Corp\",\n"
            "      \"title\": \"Software Engineer\",\n"
            "      \"duration\": \"2020-2023\",\n"
            "      \"description\": \"Developed ML models and APIs\"\n"
            "    }\n"
            "  ],\n"
            "  \"education\": [\n"
            "    {\n"
            "      \"institution\": \"University of Technology\",\n"
            "      \"degree\": \"Bachelor's\",\n"
            "      \"field\": \"Computer Science\",\n"
            "      \"year\": \"2020\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
    }


    user_prompt = {"role": "user", "content": text[:4000]}  # Truncate for token limit

    payload = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt, user_prompt],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)
    time.sleep(3)  

    if response.status_code != 200:
        raise Exception(f"❌ GROQ API error {response.status_code}: {response.text}")

    data = response.json()

    if "choices" not in data:
        raise Exception(f"❌ Unexpected GROQ response: {data}")

    content = data["choices"][0]["message"]["content"]

    json_text = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_text:
        raise Exception(f"❌ Could not extract JSON block from: {content}")
    
    try:
        return json.loads(json_text.group())
    except json.JSONDecodeError:
        print("⚠️ Warning: Model did not return valid JSON. Raw:")
        print(json_text.group())
        raise Exception(f"❌ Still could not parse JSON.")


def extract_structured_info_groq_jd(jd_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = {
        "role": "system",
        "content": (
            "You're an AI that extracts structured info from job descriptions. "
            "Return ONLY a valid JSON object with the following fields:\n"
            "- job_title (string)\n"
            "- required_skills (array of strings)\n"
            "- required_experience (string)\n"
            "- required_education (string)\n"
            "- location (string)\n\n"
            "Example:\n"
            "{\n"
            "  \"job_title\": \"Data Scientist\",\n"
            "  \"required_skills\": [\"Python\", \"SQL\", \"Machine Learning\"],\n"
            "  \"required_experience\": \"3+ years in data science or analytics\",\n"
            "  \"required_education\": \"Bachelor's or higher in Computer Science or related field\",\n"
            "  \"location\": \"Delhi, India\"\n"
            "}"
        )
    }

    user_prompt = {"role": "user", "content": jd_text[:4000]}

    payload = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt, user_prompt],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)
    time.sleep(1)  # Sleep for 1 second to avoid hitting rate/token limits

    if response.status_code != 200:
        raise Exception(f"❌ GROQ API error {response.status_code}: {response.text}")

    data = response.json()

    if "choices" not in data:
        raise Exception(f"❌ Unexpected GROQ response: {data}")

    content = data["choices"][0]["message"]["content"]

    json_text = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_text:
        raise Exception(f"❌ Could not extract JSON block from: {content}")
    
    try:
        return json.loads(json_text.group())
    except json.JSONDecodeError:
        print("⚠️ Warning: Model did not return valid JSON. Raw:")
        print(json_text.group())
        raise Exception(f"❌ Still could not parse JSON.")



