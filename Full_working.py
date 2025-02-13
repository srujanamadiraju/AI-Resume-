import streamlit as st
import pdfplumber
import docx
import json
import re
import chromadb
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

# Initialize ChromaDB (you are not storing it again, now it is stored on the disk)
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

# Extract resume details using LLM
def extract_resume_details(text):
    prompt = f"""
    Extract the following details from the given resume text and return a valid JSON object:
    - Name
    - Email
    - Phone Number
    - Skills
    - Experience (in years)
    - Job Role
    - Domain
    
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



# Retrieve similar resumes from ChromaDB
def retrieve_similar_resumes(query, top_k=3):
    return vectorstore.similarity_search(query, k=top_k)

# Generate a new ATS-friendly resume
def generate_resume(details):
    prompt = f"""
    Generate an ATS-friendly resume based on the following details:
    {json.dumps(details, indent=2)}
    
    The resume should be structured professionally with sections for Summary, Experience, Skills, and Education.
    """
    return llm.invoke(prompt).content

# Streamlit UI
st.title("AI Resume Generator")

option = st.radio("Choose an option:", ["Generate New Resume", "Modify Existing Resume"])

if option == "Generate New Resume":
    st.subheader("Enter Your Details")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    skills = st.text_area("Skills (comma-separated)")
    experience = st.text_input("Years of Experience")
    job_role = st.text_input("Job Role")
    domain = st.text_input("Domain (e.g., IT, Healthcare)")

    if st.button("Generate Resume"):
        user_details = {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills.split(","),
            "experience": experience,
            "job_role": job_role,
            "domain": domain
        }
        resume_text = generate_resume(user_details)
        st.subheader("Generated Resume")
        st.text_area("", resume_text, height=400)

elif option == "Modify Existing Resume":
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    target_job_role = st.text_input("Target Job Role")

    if uploaded_file and target_job_role and st.button("Modify Resume"):
        extracted_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_docx(uploaded_file)
        extracted_details = extract_resume_details(extracted_text)
        extracted_details["job_role"] = target_job_role
        
        retrieved_resumes = retrieve_similar_resumes(target_job_role)
        context = "\n\n".join([doc.page_content for doc in retrieved_resumes])
        
        final_resume = generate_resume({**extracted_details, "context": context})
        st.subheader("Modified Resume")
        st.text_area("", final_resume, height=400)
