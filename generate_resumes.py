from fpdf import FPDF

class ResumePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Resume", ln=True, align="C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()

def sanitize_text(text):
    return text.replace("–", "-").replace("’", "'")

def create_resume_pdf(filename, resume_data):
    pdf = ResumePDF()
    pdf.add_page()
    for section, content in resume_data.items():
        pdf.chapter_title(sanitize_text(section))
        pdf.chapter_body(sanitize_text(content))
    pdf.output(filename)

# 5 New Resumes
resumes = [
    {
        "filename": "Resume_Ishaan_Tyagi.pdf",
        "data": {
            "Name & Contact": "Ishaan Tyagi\nEmail: ishaan.tyagi.eng@gmail.com\nPhone: +91-9765123456\nLinkedIn: linkedin.com/in/ishaantyagi",
            "Professional Summary": "Software Engineer with 4 years of experience in scalable backend systems and interest in ML pipelines.",
            "Work Experience": (
                "Backend Engineer – Zeta | Mar 2021 – Present\n"
                "- Built microservices to manage payroll APIs.\n"
                "- Integrated real-time fraud detection with Kafka.\n\n"
                "Software Developer – Capgemini | Jan 2019 – Feb 2021\n"
                "- Developed REST APIs and monitored health with Prometheus + Grafana."
            ),
            "Skills": "Java, Spring Boot, Kafka, Redis, Docker, AWS, Python, Git",
            "Education": "B.Tech in Computer Engineering\nDTU, 2014 – 2018"
        }
    },
    {
        "filename": "Resume_Meenakshi_Patel.pdf",
        "data": {
            "Name & Contact": "Meenakshi Patel\nEmail: meenakshi.patel.analytics@gmail.com\nPhone: +91-9955123487\nLinkedIn: linkedin.com/in/meenakshipatel",
            "Professional Summary": "Data Analyst with 3.5 years of experience in telecom and retail. Strong in SQL, dashboarding, and automation.",
            "Work Experience": (
                "Senior Analyst – Jio Platforms | Feb 2022 – Present\n"
                "- Developed churn insights using SQL procedures.\n\n"
                "Data Analyst – Future Group | May 2019 – Jan 2022\n"
                "- Created Power BI dashboards for 70+ stores."
            ),
            "Skills": "SQL, Power BI, Excel, Python, Tableau, Google Sheets",
            "Education": "B.Sc. in Statistics\nSt. Xavier’s Mumbai, 2016 – 2019"
        }
    },
    {
        "filename": "Resume_Tanmay_Kulkarni.pdf",
        "data": {
            "Name & Contact": "Tanmay Kulkarni\nEmail: tanmay.kulkarni.ml@gmail.com\nPhone: +91-9823012345\nGitHub: github.com/tkulkarni",
            "Professional Summary": "MLOps Engineer experienced in CI/CD, MLflow tracking, and Kubernetes deployments.",
            "Work Experience": (
                "MLOps Engineer – TuringMinds | Jun 2022 – Present\n"
                "- Set up Dockerized jobs in Kubeflow.\n"
                "- Managed retraining using Airflow + S3.\n\n"
                "Intern – Persistent Systems | Jan 2022 – May 2022\n"
                "- Built Jenkins-based ML pipeline."
            ),
            "Skills": "Docker, Kubernetes, MLflow, Airflow, Jenkins, GCP, Bash, Python",
            "Education": "M.Tech in AI and ML\nVJTI Mumbai, 2020 – 2022"
        }
    },
    {
        "filename": "Resume_Shivangi_Rana.pdf",
        "data": {
            "Name & Contact": "Shivangi Rana\nEmail: shivangi.rana.ds@gmail.com\nPhone: +91-9912345678\nPortfolio: shivangirana.dev",
            "Professional Summary": "Data Science fresher with internship experience in NLP, TF-IDF, and resume matching.",
            "Work Experience": (
                "Intern – Prodigy InfoTech | Jan 2024 – Apr 2024\n"
                "- Built resume parser using NLTK.\n"
                "- Developed match scoring tool using cosine similarity."
            ),
            "Skills": "Python, NLTK, Pandas, TF-IDF, Cosine Similarity, Scikit-learn",
            "Education": "B.Tech in AI & DS\nUPES Dehradun, 2020 – 2024"
        }
    },
    {
        "filename": "Resume_Devansh_Bhatt.pdf",
        "data": {
            "Name & Contact": "Devansh Bhatt\nEmail: devansh.bhatt.coding@gmail.com\nPhone: +91-9001234567\nGitHub: github.com/devbhatt",
            "Professional Summary": "Competitive programmer and backend web dev skilled in C++, Flask, and PostgreSQL.",
            "Work Experience": (
                "Software Intern – CodeNation | Dec 2023 – Mar 2024\n"
                "- Built backend for contest scoring system.\n"
                "- Developed C++ modules for runtime analysis."
            ),
            "Skills": "C++, Python, DSA, Flask, PostgreSQL, Git",
            "Education": "B.Tech in Computer Science\nIIIT Hyderabad, 2021 – 2025 (ongoing)"
        }
    }
]

# Generate all 5 PDFs
for resume in resumes:
    create_resume_pdf(resume["filename"], resume["data"])

print("✅ All 5 additional resumes generated successfully.")
