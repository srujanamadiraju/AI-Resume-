import streamlit as st
import os
import tempfile
from extractors import (extract_text_from_pdf, extract_text_from_docx, extract_name, extract_email, 
                        extract_phone, extract_skills, extract_experience, extract_job_role, 
                        extract_domain)

st.title("Information Extraction")

st.markdown("Upload your resume and let AI extract key details!")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(temp_file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(temp_file_path)
    else:
        st.error("Unsupported file type")
        st.stop()

    # Extract key details
    name = extract_name(extracted_text)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)
    experience = extract_experience(extracted_text)
    job_role = extract_job_role(extracted_text)
    domain = extract_domain(extracted_text)

    # Display results
    st.subheader("Extracted Information")
    st.write(f"**Name:** {name}")
    st.write(f"**Email:** {email}")
    st.write(f"**Phone:** {phone}")
    st.write(f"**Skills:** {skills}")
    st.write(f"**Experience:** {experience}")
    st.write(f"**Job Role:** {job_role}")
    st.write(f"**Domain:** {domain}")

    # Clean up temp file
    os.remove(temp_file_path)
