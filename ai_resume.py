import streamlit as st
import pdfplumber
import docx
import chromadb
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize LLM
llm = ChatGroq(
    groq_api_key="",
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(client=chroma_client, embedding_function=embedding_function)

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

# Generate a new ATS-friendly resume based on user input
def generate_resume(details, job_description):
    relevant_projects = fetch_relevant_projects(job_description)

    project_section = "\n".join(
        f"**{proj['title']}**\n{proj['description']}" for proj in relevant_projects
    )

    prompt = f"""
    Generate a professional ATS-friendly resume based on the following details:
    {details}
    Tailor the resume to align with the following job description:
    {job_description}
    Include the following relevant projects in the resume:
    {project_section}
    Ensure the output follows a structured professional resume format with sections for Contact Information, Summary, Education, Skills, Experience, Projects, Achievements, and Certifications.
    If any details are missing, skip that section in the resume (for example, freshers might not have experience). 
    Strictly remove "Here's an ATS-friendly resume based on the provided details:" line at the beginning and the note section placed last in the PDF.
    Make the headings bold and the content in normal font. Draw a line after each section.
    """
    return llm.invoke(prompt).content

# Modify existing resume while keeping the original format
def modify_resume(text, job_description):
    relevant_projects = fetch_relevant_projects(job_description)

    project_section = "\n".join(
        f"**{proj['title']}**\n{proj['description']}" for proj in relevant_projects
    )

    prompt = f"""
    Modify the following resume to be ATS-friendly according to the given job description:
    Resume Text:
    {text}
    Job Description:
    {job_description}
    Include the following relevant projects in the resume:
    {project_section}
    Ensure the original format, structure, and layout remain unchanged. Only update the content to be more ATS-friendly by improving keyword relevance and alignment with the job description.
    Do not add any additional content or sections that were not present in the original resume. Give only the resume, no need for any explanation. The resume should be ready to apply for a job. Do not add the line "Here's the modified ATS-friendly resume" and the note at the last in the PDF.
    Strictly remove "Here's an ATS-friendly resume based on the provided details:" line at the beginning and the note section placed last in the PDF.
    Make the headings bold and visible easily. Draw a line after each section.
    """
    return llm.invoke(prompt).content

# Convert text to PDF while keeping formatting
def text_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    text = text.encode("latin-1", "ignore").decode("latin-1")
    pdf.multi_cell(0, 10, text)
    pdf.output(filename, "F")
    
def fetch_relevant_projects(job_description, num_projects=3):
    query_results = vectorstore.similarity_search(job_description, k=num_projects)
    return [{"title": doc.metadata["title"], "description": doc.page_content} for doc in query_results]

# Streamlit UI
st.title("AI Resume Generator")

option = st.radio("Choose an option:", ["Upload Basic Details & Job Description", "Upload Resume & Job Description"])

if option == "Upload Basic Details & Job Description":
    st.subheader("Enter Your Details")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    education = st.text_area("Education (School, College, Degree)")
    skills = st.text_area("Skills (comma-separated)")
    experience = st.text_area("Experience")
    achievements = st.text_area("Achievements")
    certifications = st.text_area("Certifications")
    job_description = st.text_area("Job Description")

    if st.button("Generate Resume"):
        user_details = {
            "name": name,
            "email": email,
            "phone": phone,
            "education": education,
            "skills": skills.split(","),
            "experience": experience,
            "achievements": achievements,
            "certifications": certifications,
        }
        resume_text = generate_resume(user_details, job_description)
        st.subheader("Preview Generated Resume")
        st.text_area("", resume_text, height=400)
        pdf_filename = "generated_resume.pdf"
        text_to_pdf(resume_text, pdf_filename)
        st.download_button("Download Resume", open(pdf_filename, "rb"), file_name=pdf_filename, mime="application/pdf")

if option == "Upload Resume & Job Description":
    st.subheader("Upload Resume & Enter Job Description")
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    job_description = st.text_area("Job Description")

    if uploaded_file and job_description and st.button("Modify Resume"):
        extracted_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_docx(uploaded_file)
        modified_resume = modify_resume(extracted_text, job_description)
        st.subheader("Preview Modified Resume")
        st.text_area("", modified_resume, height=400)
        pdf_filename = "modified_resume.pdf"
        text_to_pdf(modified_resume, pdf_filename)
        st.download_button("Download Modified Resume", open(pdf_filename, "rb"), file_name=pdf_filename, mime="application/pdf")
