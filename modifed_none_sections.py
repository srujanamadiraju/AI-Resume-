import streamlit as st
import pdfplumber
import docx
import chromadb
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import re 

llm = ChatGroq(
    groq_api_key="",
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(client=chroma_client, embedding_function=embedding_function)

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text(layout=True) for page in pdf.pages if page.extract_text(layout=True))
    return text

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
    If any details are missing, skip that section in the resume (for example, freshers might not have experience). If the entry for a section says 'None' or 'none' or just left blank then don't include the section in the resume.
    Strictly remove "Here's an ATS-friendly resume based on the provided details:" line at the beginning and the note section placed last in the PDF.
    Make the headings bold and the content in normal font. Draw a line after each section.
    """
    raw_text = llm.invoke(prompt).content
    cleaned_text = clean_resume_text(raw_text)
    return cleaned_text 

def modify_resume(text, job_description):
    relevant_projects = fetch_relevant_projects(job_description)

    # Debug: Show projects in Streamlit
    if relevant_projects:
        st.subheader("🔹 Relevant Projects Found:")
        for proj in relevant_projects:
            st.markdown(f"<p style='font-size:12px;'><b>{proj['title']}</b><br>{proj['description']}</p>", unsafe_allow_html=True)

    existing_projects_section = extract_existing_projects(text)

    # Format projects to include in the prompt
    project_section = "\n".join(
        f"**{proj['title']}**\n{proj['description']}" for proj in relevant_projects
    ) if relevant_projects else "**No relevant projects found.**"

    # Ensure missing projects are added
    final_project_section = merge_projects(existing_projects_section, project_section)

    prompt = f"""
    Modify the following resume to be ATS-friendly according to the given job description:
    Resume Text:
    {text}
    Job Description:
    {job_description}
    Ensure the following projects are included in the resume:
    {final_project_section}
    Ensure the original format, structure, and layout remain unchanged. Only update the content to be more ATS-friendly by improving keyword relevance and alignment with the job description.
    Do not add any additional content or sections that were not present in the original resume unless specified.
    Strictly remove "Here's an ATS-friendly resume based on the provided details:" line at the beginning and the note section placed last in the PDF.
    Make the headings bold and visible. Draw a line after each section.
    """

    return llm.invoke(prompt).content


    return modified_resume

def clean_resume_text(resume_text):
    """
    Removes empty sections from the generated resume if they contain 'None', 'none', or are blank.
    """
    cleaned_lines = []
    lines = resume_text.split("\n")
    
    filtered_sections = []
    current_section = []
    inside_section = False

    for line in lines:
        # If line is a section title (bold text)
        if "**" in line:
            # Process the previous section before starting a new one
            if current_section and not all(content.strip().lower() in ["none", "", "(no relevant experience listed)"] for content in current_section[1:]):
                filtered_sections.extend(current_section)  # Keep valid sections
                filtered_sections.append("")  
        
            # Start a new section
            current_section = [line]
            inside_section = True
        else:
            if inside_section:
                current_section.append(line)

    if current_section and not all(content.strip().lower() in ["none", "", "(no relevant experience listed)"] for content in current_section[1:]):
        filtered_sections.extend(current_section)

    return "\n".join(filtered_sections).strip()

        

def generate_pdf(text):
    """ Converts formatted resume text into a PDF file. """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    lines = text.split("\n")
    for line in lines:
        if re.match(r"^[A-Z ]{3,}$", line.strip()):  # Detects headings in ALL CAPS
            pdf.set_font("Arial", style='B', size=14)
        else:
            pdf.set_font("Arial", size=12)

        pdf.cell(200, 7, line, ln=True)

    # Save PDF as bytes for Streamlit
    import io
    pdf_output = io.BytesIO()
    pdf.output(pdf_output, 'F')
    return pdf_output.getvalue()

def extract_existing_projects(resume_text):
    match = re.search(r"(Projects|Relevant Projects)\s*([\s\S]*?)(?=\n[A-Z])", resume_text)
    return match.group(2).strip() if match else ""  # Extracts projects if found

def merge_projects(existing_projects, new_projects):
    if not existing_projects:
        return new_projects  # If no existing projects, use new ones
    return f"{existing_projects}\n\n{new_projects}"  # Append new projects

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
    # Search ChromaDB for relevant projects
    query_results = vectorstore.similarity_search_with_relevance_scores(job_description, k=num_projects)

    relevant_projects = []
    for doc, score in query_results:
        print(f"🔍 Found Project: {doc.metadata.get('title', 'Untitled')} (Score: {score})")  # Debugging
        if score > 0.7:  # Keep only highly relevant projects
            relevant_projects.append({
                "title": doc.metadata.get("title", "Untitled"),
                "description": doc.page_content
            })

    # If no relevant projects found, generate new ones
    if len(relevant_projects) < num_projects:
        print(f"⚠️ Only {len(relevant_projects)} relevant projects found. Generating {num_projects - len(relevant_projects)} new ones...")

        prompt = f"""
        Generate {num_projects - len(relevant_projects)} relevant project ideas based on the following job description.
        Each project should have a **meaningful and descriptive title**, not just 'Project 1'.

        Job Description:
        {job_description}

        Format:
        **Title:** [Descriptive Project Title]
        **Description:** [A short, detailed description of the project]
        """

        response = llm.invoke(prompt).content
        print(f"🔄 Generated Projects:\n{response}")  # Debugging

        # Parse generated response
        new_projects = []
        for project_text in response.split("\n**Title:** ")[1:]:
            lines = project_text.split("\n**Description:** ")
            if len(lines) == 2:
                title = lines[0].strip()
                description = lines[1].strip()
                new_projects.append({"title": title, "description": description})

        # Store generated projects in ChromaDB
        for project in new_projects:
            vectorstore.add_texts(
                texts=[project["description"]],
                metadatas=[{"title": project["title"]}]
            )

        relevant_projects.extend(new_projects)

    print(f"✅ Final Projects: {relevant_projects}")  # Debugging
    return relevant_projects


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
