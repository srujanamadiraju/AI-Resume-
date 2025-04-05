import streamlit as st
import json
import pdfplumber
import requests
import os
from jinja2 import Environment, FileSystemLoader

# ==== CONFIG ==== #
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = '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'  

# ==== FUNCTIONS ==== #
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_resume_info(text):
    prompt = f"""
    Extract structured resume information (name, phone, email, github, linkedin, work experience, education, skills, certifications, projects, achievements) in JSON format from the following resume text:

    === RESUME TEXT ===
    {text}

    ⚠️ Output ONLY a valid JSON object — no markdown, explanation, or extra text.
    """

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )

    result = response.json()

    # Check for API error
    if "error" in result:
        st.error(f"❌ Groq API Error: {result['error']['message']}")
        return {}

    try:
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        st.error("⚠️ Could not parse JSON from Groq response. Raw output shown below:")
        st.code(result)
        return {}

def refine_resume(info, job_description):
    prompt = f"""
    You are an AI resume assistant. Based on the following job description and resume (in JSON), refine and tailor the resume to better fit the role.

    ⚠️ Output must be a single valid JSON object only — no extra text, no markdown, no explanation.

    === Job Description ===
    {job_description}

    === Resume JSON ===
    {json.dumps(info, indent=2)}
    """

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
    )

    result = response.json()

    if "error" in result:
        st.error(f"❌ Groq API Error: {result['error']['message']}")
        return info  # fallback to original resume

    try:
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        st.error("⚠️ Could not parse JSON from model. Here's the raw output:")
        st.code(result)
        return info



def generate_cover_letter(info, job_description):
    prompt = f"""
    Generate a concise and professional cover letter based on the resume and job description below.

    === Job Description ===
    {job_description}

    === Resume JSON ===
    {json.dumps(info, indent=2)}

    Output the letter in plain text with no JSON or markdown formatting.
    """

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    result = response.json()

    if "error" in result:
        st.error(f"❌ Groq API Error: {result['error']['message']}")
        return "Cover letter generation failed due to API limits."

    return result["choices"][0]["message"]["content"]

def generate_latex(info):
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("resume.tex")
    return template.render(**info)

# ==== UI ==== #
st.set_page_config(page_title="Resume & Cover Letter Generator", layout="centered")
st.title("📄 Smart Resume & Cover Letter Generator")

uploaded_file = st.file_uploader("Upload your resume (PDF or JSON)", type=["pdf", "json"])
job_description = st.text_area("Paste the Job Description", height=200)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
        resume_info = extract_resume_info(text)
    else:
        resume_info = json.load(uploaded_file)

    st.success("✅ Resume data extracted successfully!")
    st.subheader("📋 Extracted Resume Info")
    st.json(resume_info)

    # Refine resume based on JD
    if job_description:
        with st.spinner("Refining resume for job description..."):
            resume_info = refine_resume(resume_info, job_description)
        st.success("✨ Resume tailored to job description!")

    # Cover Letter
    if st.button("Generate Cover Letter"):
        if not job_description:
            st.warning("Please paste the job description to generate a tailored cover letter.")
        else:
            with st.spinner("Generating cover letter..."):
                letter = generate_cover_letter(resume_info, job_description)
            st.subheader("✉️ Generated Cover Letter")
            st.text_area("Cover Letter", letter, height=300)

    # LaTeX resume
    if st.button("Download LaTeX Resume"):
        with st.spinner("Rendering LaTeX..."):
            latex_code = generate_latex(resume_info)
            st.code(latex_code, language="latex")

        st.download_button("📥 Download .tex file", latex_code, file_name="resume.tex", mime="text/plain")
