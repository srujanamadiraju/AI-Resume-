
import streamlit as st
import json
import pdfplumber
import requests
import os
import tempfile
from jinja2 import Environment, FileSystemLoader
import subprocess

# === CONFIG === #
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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" # Replace with your key

# === FUNCTIONS === #
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def safe_extract_json(response_text):
    try:
        start = response_text.index("{")
        end = response_text.rindex("}") + 1
        return json.loads(response_text[start:end])
    except Exception:
        return {}

def call_groq_api(prompt, temperature=0.3):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    result = response.json()

    if "error" in result:
        st.error(f"❌ Groq API Error: {result['error']['message']}")
        return {}

    return result["choices"][0]["message"]["content"]

def extract_resume_info(text):
    prompt = f"""
    Extract structured resume information (name, phone, email, github, linkedin, work experience, education, skills, certifications, projects, achievements) in JSON format from the following resume text:

    === RESUME TEXT ===
    {text}

    ⚠️ Output ONLY a valid JSON object — no markdown, explanation, or extra text.
    """
    response_text = call_groq_api(prompt, temperature=0.2)
    return safe_extract_json(response_text)

def refine_resume(info, job_description):
    prompt = f"""
    You are an AI resume assistant. Based on the following job description and resume (in JSON), refine and tailor the resume to better fit the role.

    ⚠️ Output must be a single valid JSON object only — no extra text, no markdown, no explanation.

    === Job Description ===
    {job_description}

    === Resume JSON ===
    {json.dumps(info, indent=2)}
    """
    response_text = call_groq_api(prompt, temperature=0.3)
    return safe_extract_json(response_text)

def generate_cover_letter(info, job_description):
    prompt = f"""
    Generate a concise and professional cover letter based on the resume and job description below.

    === Job Description ===
    {job_description}

    === Resume JSON ===
    {json.dumps(info, indent=2)}

    Output the letter in plain text with no JSON or markdown formatting.
    """
    return call_groq_api(prompt, temperature=0.7)

def render_latex_to_pdf(resume_data):
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("resume.tex")

    latex_code = template.render(**resume_data)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        pdf_path = os.path.join(tmpdir, "resume.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                return f.read()

        st.error("Failed to generate PDF. LaTeX error:")
        st.code(result.stdout.decode())
        return None

# === STREAMLIT UI === #
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

    if resume_info:
        st.success("✅ Resume data extracted successfully!")
        st.subheader("📋 Extracted Resume Info")
        st.json(resume_info)
    else:
        st.error("Failed to extract valid JSON. Check the API response.")
        st.stop()

    if job_description:
        with st.spinner("Refining resume for job description..."):
            resume_info = refine_resume(resume_info, job_description)
        st.success("✨ Resume tailored to job description!")

    if st.button("Generate Cover Letter"):
        if not job_description:
            st.warning("Please paste the job description to generate a tailored cover letter.")
        else:
            with st.spinner("Generating cover letter..."):
                letter = generate_cover_letter(resume_info, job_description)
            st.subheader("✉️ Generated Cover Letter")
            st.text_area("Cover Letter", letter, height=300)

    if st.button("Download PDF Resume"):
        with st.spinner("Compiling LaTeX to PDF..."):
            pdf_bytes = render_latex_to_pdf(resume_info)
            if pdf_bytes:
                st.download_button(
                    "📥 Download PDF",
                    data=pdf_bytes,
                    file_name="resume.pdf",
                    mime="application/pdf"
                )
