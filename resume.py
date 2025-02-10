%%writefile C:/Users/madir/OneDrive/Desktop/resume_app.py
import streamlit as st
import pdfplumber
import docx
import re
import spacy
import pypandoc
import os

nlp = spacy.load("en_core_web_sm")

SKILLS_LIST = {"Python", "Java", "Machine Learning", "Deep Learning", "Data Science", "SQL", "JavaScript", "AWS", "React", "TensorFlow", "Web Scraping", "Google PaLM API", "LangChain", "EDA", "Unity", "HTML", "GitHub", "C programming"}
JOB_ROLES = {"Software Engineer", "Data Scientist", "Machine Learning Engineer", "Project Manager", "AI Researcher", "Data Analyst", "Backend Developer", "Frontend Developer"}
DOMAINS = {"Healthcare", "Finance", "E-commerce", "Education", "Cybersecurity", "Robotics", "Blockchain"}

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

import io
from docx2pdf import convert
import tempfile

def convert_docx_to_pdf(docx_file):
    """Convert .docx to .pdf and return the PDF file path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        temp_docx.write(docx_file.read())
        temp_docx_path = temp_docx.name

    temp_pdf_path = temp_docx_path.replace(".docx", ".pdf")
    convert(temp_docx_path, temp_pdf_path)  # Convert to PDF
    return temp_pdf_path



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

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    phone_pattern = r'\b(?:\+?\d{1,3})?\s?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Not Found"

def extract_skills(text):
    found_skills = {skill for skill in SKILLS_LIST if skill.lower() in text.lower()}
    return ", ".join(sorted(found_skills)) if found_skills else "Not Found"

def extract_experience(text):
    exp_pattern = r'(?i)(\d+)\s*(?:\+?\s*years?|months?)\s*(?:of experience|experience|working)?'
    match = re.search(exp_pattern, text)
    return f"{match.group(1)} years" if match else "0 years"

def extract_job_role(text):
    doc = nlp(text)
    found_roles = set()

    # Check for predefined job roles
    for token in doc:
        if token.text.lower() in {role.lower() for role in JOB_ROLES}:  # Ensure case-insensitive match
            found_roles.add(token.text)

    # Context-based detection from the "About Me" section
    about_me_patterns = {
        "data science professional", 
        "machine learning engineer", 
        "software engineer", 
        "data analyst"
    }
    
    for phrase in about_me_patterns:
        if phrase in text.lower():
            found_roles.add(phrase.title())

    return ", ".join(sorted(found_roles)) if found_roles else "Not Specific"


def extract_domain(text):
    found_domains = {domain for domain in DOMAINS if domain.lower() in text.lower()}
    return ", ".join(sorted(found_domains)) if found_domains else "Not Found"

st.title("Resume Parser")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        pdf_path = convert_docx_to_pdf(uploaded_file)  # Convert .docx → .pdf
        extracted_text = extract_text_from_pdf(pdf_path)  # Extract from converted PDF
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
