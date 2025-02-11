import streamlit as st
import pdfplumber
import docx
import re
import spacy
from docx2pdf import convert
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Predefined Skills, Job Roles, and Domains
SKILLS_LIST = {"Python", "Java", "Machine Learning", "Deep Learning", "Data Science", "SQL", "JavaScript", "AWS", "React", "TensorFlow", "Web Scraping", "Google PaLM API", "LangChain", "EDA", "Unity", "HTML", "GitHub", "C programming"}
JOB_ROLES = {"Software Engineer", "Data Scientist", "Machine Learning Engineer", "Project Manager", "AI Researcher", "Data Analyst", "Backend Developer", "Frontend Developer"}
DOMAINS = {"Healthcare", "Finance", "E-commerce", "Education", "Cybersecurity", "Robotics", "Blockchain"}

# Extract text from PDF with better layout handling
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text(layout=True) for page in pdf.pages if page.extract_text(layout=True))
    return text

# Extract text from DOCX, including tables
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = []
    for para in doc.paragraphs:
        text.append(para.text.strip())
    
    for table in doc.tables:
        for row in table.rows:
            text.append(" ".join(cell.text.strip() for cell in row.cells))
    
    return "\n".join(text)

# Convert DOCX to PDF if needed
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
import re
from datetime import datetime

def extract_experience(text):
    experience_patterns = [
        r'(?i)([A-Za-z\s-]+)\s+at\s+([\w\s&-]+)\s+\((\d{4})-(\d{4}|\bPresent\b|\bCurrent\b)\)',  # Role at Company (YYYY-YYYY/Present/Current)
        r'(?i)([A-Za-z\s-]+)\s+at\s+([\w\s&-]+),?\s+from\s+(\d{4})\s+to\s+(\d{4}|\bPresent\b|\bCurrent\b)',  # Role at Company from YYYY to YYYY/Present/Current
        r'(?i)(\d{4})\s*[-–]\s*(\bCurrent\b|\bPresent\b)',  # YYYY - Current
        r'(?i)([A-Za-z]+)\s+(\d{4})\s*[-–]\s*([A-Za-z]+)?\s*(\d{4}|\bPresent\b|\bCurrent\b)?'  # Month Year - Month Year / Month Year - Present
    ]
    
    total_experience = 0
    current_year = datetime.now().year
    current_month = datetime.now().month
    seen_periods = set()  # To prevent duplicate counting

    # Month mapping for conversion
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }

    for pattern in experience_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 4:  # Formats with Role, Company, Start Year, End Year
                role, company, start_year, end_year = match
            elif len(match) == 3:  # Formats without role (e.g., "Worked at Company from YYYY-Present")
                company, start_year, end_year = match
                role = ""  # No role in this case
            elif len(match) == 2:  # "YYYY - Current" format
                start_year, end_year = match
                role, company = "", ""  # No role or company
            elif len(match) == 5:  # "Month Year - Month Year / Month Year - Present" format
                start_month, start_year, end_month, end_year = match[0], match[1], match[2], match[3]

                # Convert month names to numbers
                start_month_num = month_map.get(start_month.lower(), 1)
                end_month_num = month_map.get(end_month.lower(), 1) if end_month else start_month_num

                # Convert years to integers
                start_year = int(start_year)
                end_year = current_year if end_year.lower() in ["present", "current"] else int(end_year)

                # Avoid duplicate experience periods
                if (start_year, end_year, start_month_num, end_month_num) in seen_periods:
                    continue
                seen_periods.add((start_year, end_year, start_month_num, end_month_num))

                # Calculate experience in months and convert to years
                experience_months = (end_year - start_year) * 12 + (end_month_num - start_month_num)
                years_of_experience = max(0, experience_months // 12)
                total_experience += years_of_experience
                continue

            # Exclude internships and projects
            if "intern" in role.lower() or "project" in role.lower():
                continue

            try:
                start_year = int(start_year)
                end_year = current_year if end_year.lower() in ["present", "current"] else int(end_year)

                # Avoid duplicate experience periods
                if (start_year, end_year) in seen_periods:
                    continue
                seen_periods.add((start_year, end_year))

                # Calculate experience duration
                years_of_experience = max(0, end_year - start_year)
                total_experience += years_of_experience
            except ValueError:
                continue  # Skip invalid year formats

    return f"{total_experience} years" if total_experience > 0 else "0 years"



# Extract Job Role
def extract_job_role(text):
    doc = nlp(text)
    found_roles = set()
    for token in doc:
        if token.text in JOB_ROLES:
            found_roles.add(token.text)
    
    about_me_patterns = ["Software Engineer", "Data Scientist", "Machine Learning Engineer", "AI Engineer", 
    "Deep Learning Engineer", "Data Analyst", "Business Analyst", "Backend Developer", 
    "Frontend Developer", "Full Stack Developer", "Cloud Engineer", "DevOps Engineer", 
    "Cybersecurity Analyst", "Embedded Systems Engineer", "Blockchain Developer", 
    "Computer Vision Engineer", "NLP Engineer", "Product Manager", "QA Engineer", 
    "Automation Engineer", "Data Engineer", "Database Administrator", "Software Architect", 
    "System Administrator", "IT Support Engineer", "Game Developer", "Mobile App Developer", 
    "AR/VR Developer", "Site Reliability Engineer", "AI Research Scientist", "Big Data Engineer", 
    "BI Analyst", "Security Engineer", "Network Engineer", "IoT Engineer", 
    "Technical Support Engineer", "Research Scientist", "Technical Program Manager", 
    "DataOps Engineer", "MLOps Engineer", "Robotics Engineer", "Quantum Computing Engineer",]
    for phrase in about_me_patterns:
        if phrase in text.lower():
            found_roles.add(phrase.title())
    
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
        os.remove(temp_pdf)  # Clean up temp file
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
