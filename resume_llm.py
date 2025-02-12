import streamlit as st
import pdfplumber
import docx
import os
from langchain_groq import ChatGroq

# Initialize LLM
llm = ChatGroq(
    groq_api_key="use_your_key",
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text(layout=True) for page in pdf.pages if page.extract_text(layout=True))
    return text

# Extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "\n".join(para.text.strip() for para in doc.paragraphs if para.text.strip())
    return text

# Function to process resume text using LLM
import json
import re

def extract_resume_details(text):
    prompt = f"""
    Extract the following details from the given resume text and return a valid JSON object:
    - Name
    - Email
    - Phone Number
    - Skills
    - Experience (in years,do not include projects or internships,if nothing found,return "0 years")
    - Job Role (Specified in the resume,if nothing found,return "Not found")
    - Domain (For example: Finance, Healthcare,IT,Business,Fashion etc. If nothing found, return "Not found")
    
    Resume Text:
    {text}
    
    Return only valid JSON output without any extra text, explanation, or formatting. 
    Example output format:
    {{
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "+1234567890",
        "skills": ["Python", "Machine Learning", "SQL"],
        "experience": "5 years",
        "job_role": "Data Scientist",
        "domain": "Finance"
    }}
    """
    response = llm.invoke(prompt).content

    # Extract JSON using regex (to handle any extra text)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    
    if json_match:
        json_text = json_match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            st.error("JSON Parse Error: Unable to decode valid JSON.")
            return {}
    else:
        st.error("JSON Parse Error: No valid JSON found in the response.")
        return {}


st.title("AI Resume Parser with LLM")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    extracted_text = ""
    
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()
    
    # Get extracted details from LLM
    extracted_details = extract_resume_details(extracted_text)

    if extracted_details:
        st.subheader("Extracted Information")
        st.json(extracted_details)

