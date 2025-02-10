%%writefile C:/Users/madir/OneDrive/Desktop/resume_app.py
import streamlit as st
import re
import fitz  
import docx
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

skills_list = {"Python", "Java", "Machine Learning", "Deep Learning", "Data Science", "AWS", "SQL", "JavaScript", "React", "TensorFlow", "Exploratory Data Analysis", "Web Scraping", "Explainable AI", "Statistical Analysis", "Google PaLM API", "LangChain", "EDA", "Matplotlib", "Seaborn"}
job_roles = {"Software Engineer", "Data Scientist", "Machine Learning Engineer", "Project Manager", "AI Researcher", "Data Science Professional", "Data Analyst"}
domains = {"Healthcare", "Finance", "E-commerce", "Education", "Cybersecurity", "Robotics", "Sustainability", "Blockchain"}

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_name(text):
    # Extract the first few lines (assuming name is in the header)
    lines = text.strip().split("\n")[:5]  # Look at the first 5 lines
    
    # Use regex to find the first capitalized words (likely a name)
    name_pattern = r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+)+'
    for line in lines:
        match = re.search(name_pattern, line.strip())
        if match:
            return match.group(0)
    
    # Fallback: Use spaCy's entity recognition
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return "Not Found"

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not Found"

def extract_phone(text):
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not Found"

def extract_skills(text):
    doc = nlp(text)
    found_skills = set()
    for token in doc:
        if token.text in skills_list:
            found_skills.add(token.text)
    
    # Also checking for multi-word skills
    for phrase in skills_list:
        if phrase.lower() in text.lower():
            found_skills.add(phrase)
    
    return ", ".join(found_skills) if found_skills else "Not Found"

def extract_experience(text):
    experience_pattern = r'(?i)(\d+\s*(?:years?|months?)\s*(?:of)?\s*(?:experience|working)?)'
    experience = re.findall(experience_pattern, text)
    if experience:
        return ", ".join(experience)
    
    # Additional check for project timelines
    year_pattern = r'\b(\d{4})\b'
    years = re.findall(year_pattern, text)
    if years:
        min_year, max_year = min(map(int, years)), max(map(int, years))
        return f"{max_year - min_year} years (estimated from projects)"
    return "Not Found"

def extract_job_role(text):
    doc = nlp(text)
    found_roles = set()
    for token in doc:
        if token.text in job_roles:
            found_roles.add(token.text)
    
    # Context-based detection from "About Me" section
    about_me_patterns = [
        "data science professional", "machine learning engineer", "software engineer", "data analyst"
    ]
    for phrase in about_me_patterns:
        if phrase in text.lower():
            found_roles.add(phrase.title())
    
    return ", ".join(found_roles) if found_roles else "Not Found"

def extract_domain(text):
    found_domains = set()
    for phrase in domains:
        if phrase.lower() in text.lower():
            found_domains.add(phrase)
    return ", ".join(found_domains) if found_domains else "Not Found"

st.title("Resume Upload & Info Extraction")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()
    
    name = extract_name(extracted_text)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)
    experience = extract_experience(extracted_text)
    job_role = extract_job_role(extracted_text)
    domain = extract_domain(extracted_text)
    
    st.subheader("Extracted Information")
    st.write(f"**Name:** {name}")
    st.write(f"**Email:** {email}")
    st.write(f"**Phone:** {phone}")
    st.write(f"**Skills:** {skills}")
    st.write(f"**Experience:** {experience}")
    st.write(f"**Job Role:** {job_role}")
    st.write(f"**Domain:** {domain}")
