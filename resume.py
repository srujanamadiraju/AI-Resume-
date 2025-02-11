import streamlit as st
import pdfplumber
import docx
import re
import spacy
from docx2pdf import convert
import os
from datetime import datetime

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Predefined Skills, Job Roles, and Domains
SKILLS_LIST = {
    "Python", "Java", "Machine Learning", "Deep Learning", "Data Science", "SQL", "JavaScript",
    "AWS", "React", "TensorFlow", "Web Scraping", "Google PaLM API", "LangChain", "EDA",
    "C", "C++", "HTML", "CSS", "PHP", "Node.js", "Angular", "Vue.js", "Django", "Flask",
    "Docker", "Kubernetes", "JIRA", "Git", "MySQL", "PostgreSQL", "MongoDB", "Power BI",
    "Security Audits", "Networking", "Cloud Computing", "Scrum", "Machine Learning", "NLP",
    "CI/CD", "Automation", "DevOps", "Data Analysis", "Hadoop", "Linux"
}

JOB_ROLES = {
    "Software Engineer", "Data Scientist", "Machine Learning Engineer", "Project Manager",
    "AI Researcher", "Data Analyst", "Backend Developer", "Frontend Developer"
}

DOMAINS = {"Healthcare", "Finance", "E-commerce", "Education", "Cybersecurity", "Robotics", "Blockchain"}

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text(layout=True) for page in pdf.pages if page.extract_text(layout=True))
    return text

# Extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = [para.text.strip() for para in doc.paragraphs]
    
    for table in doc.tables:
        for row in table.rows:
            text.append(" ".join(cell.text.strip() for cell in row.cells))
    
    return "\n".join(text)

# Convert DOCX to PDF
def convert_docx_to_pdf(docx_file):
    temp_pdf = "temp_resume.pdf"
    convert(docx_file, temp_pdf)
    return temp_pdf

# Extract Name
def extract_name(text):
    lines = text.split("\n")
    first_non_empty_line = next((line.strip() for line in lines if line.strip()), "")
    
    if 2 <= len(first_non_empty_line.split()) <= 4 and re.match(r'^[A-Za-z\s]+$', first_non_empty_line):
        return first_non_empty_line
    
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    return "Not Found"

# Extract Email
def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Not Found"

# Extract Phone Number
def extract_phone(text):
    phone_pattern = r'\b(?:\+?\d{1,3})?\s?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Not Found"

# Extract Skills
def extract_skills(text):
    found_skills = {skill for skill in SKILLS_LIST if skill.lower() in text.lower()}
    return ", ".join(sorted(found_skills)) if found_skills else "Not Found"

# Extract Experience
def extract_experience(text):
    current_year = datetime.now().year
    total_experience = 0
    seen_periods = set()

    experience_patterns = [
        r'(?i)(\b\d{4}\b)\s*[-–]\s*(\b\d{4}|\bPresent\b|\bCurrent\b)',
        r'(?i)(\b\d{4}\b)\s+to\s+(\b\d{4}|\bPresent\b|\bCurrent\b)',
        r'(?i)([A-Za-z]+\s+\d{4})\s*[-–]\s*([A-Za-z]+\s+\d{4}|\bPresent\b|\bCurrent\b)'
    ]

    education_keywords = ["bachelor", "master", "phd", "diploma", "college", "university", "education"]
    internship_keywords = ["intern", "internship", "virtual internship"]

    # Ensure experience section exists
    if not text or not re.search(r'(?i)\b(work\s+experience|professional\s+experience|employment\s+history)\b', text):
        return "0 years"

    for pattern in experience_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                start_year, end_year = match
                start_year = int(re.search(r'\d{4}', start_year).group())
                end_year = current_year if re.search(r'(?i)present|current', end_year) else int(re.search(r'\d{4}', end_year).group())

                experience_text_snippet = text.lower()
                snippet_start = max(text.lower().find(str(start_year)) - 50, 0)
                snippet_end = min(text.lower().find(str(end_year)) + 50, len(text))
                context_snippet = text.lower()[snippet_start:snippet_end]

                if any(keyword in context_snippet for keyword in internship_keywords):
                    continue

                if (start_year, end_year) not in seen_periods:
                    seen_periods.add((start_year, end_year))
                    total_experience += max(0, end_year - start_year)

            except ValueError:
                continue

    return f"{total_experience} years" if total_experience > 0 else "0 years"

# Extract Job Role
def extract_job_role(text):
    found_roles = {role for role in JOB_ROLES if role.lower() in text.lower()}
    return ", ".join(found_roles) if found_roles else "Not Specified"

# Extract Domain
def extract_domain(text):
    found_domains = {domain for domain in DOMAINS if domain.lower() in text.lower()}
    return ", ".join(sorted(found_domains)) if found_domains else "Not Found"

# Streamlit App
st.title("Resume Parser")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    extracted_text = ""

    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        temp_pdf = convert_docx_to_pdf(uploaded_file)
        extracted_text = extract_text_from_pdf(temp_pdf)
        os.remove(temp_pdf)
    else:
        st.error("Unsupported file type")
        st.stop()

    # Extract Information
    name = extract_name(extracted_text)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)
    experience = extract_experience(extracted_text)
    job_role = extract_job_role(extracted_text)
    domain = extract_domain(extracted_text)

    # Display Results
    st.subheader("Extracted Information")
    st.write(f"**Name:** {name}")
    st.write(f"**Email:** {email}")
    st.write(f"**Phone:** {phone}")
    st.write(f"**Skills:** {skills}")
    st.write(f"**Experience:** {experience}")
    st.write(f"**Job Role:** {job_role}")
    st.write(f"**Domain:** {domain}")
