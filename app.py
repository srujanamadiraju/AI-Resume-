# import streamlit as st
# import json
# import pdfplumber
# import requests
# import os
# from jinja2 import Environment, FileSystemLoader
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import CountVectorizer
# import numpy as np

# # === CONFIG === #
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# GROQ_API_KEY = "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"  # Replace with your key

# # === FUNCTIONS === #
# st_model = SentenceTransformer('all-MiniLM-L6-v2')

# def embedding_similarity(doc1: str, doc2: str) -> float:
#     embeddings = st_model.encode([doc1, doc2], convert_to_tensor=False)
#     return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

# def jaccard_similarity(doc1: str, doc2: str) -> float:
#     vec = CountVectorizer().fit_transform([doc1, doc2])
#     vec = vec.toarray()
#     intersection = np.minimum(vec[0], vec[1]).sum()
#     union = np.maximum(vec[0], vec[1]).sum()
#     return intersection / union if union != 0 else 0.0

# def combined_similarity(doc1: str, doc2: str) -> float:
#     emb_score = embedding_similarity(doc1, doc2)
#     jac_score = jaccard_similarity(doc1, doc2)
#     return round((emb_score + jac_score) / 2, 4)

# def extract_text_from_pdf(uploaded_file):
#     with pdfplumber.open(uploaded_file) as pdf:
#         return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# def safe_extract_json(response_text):
#     try:
#         start = response_text.index("{")
#         end = response_text.rindex("}") + 1
#         return json.loads(response_text[start:end])
#     except Exception:
#         return {}

# def call_groq_api(prompt, temperature=0.3):
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "llama3-8b-8192",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": temperature
#     }
#     response = requests.post(GROQ_API_URL, headers=headers, json=payload)
#     result = response.json()
#     if "error" in result:
#         st.error(f"❌ Groq API Error: {result['error']['message']}")
#         return {}
#     return result["choices"][0]["message"]["content"]

# def extract_resume_info(text):
#     prompt = f"""
#     Extract structured resume information (name, phone, email, github, linkedin, work experience, education, skills, certifications, projects, achievements) in JSON format from the following resume text:

#     === RESUME TEXT ===
#     {text}

#     ⚠️ Output ONLY a valid JSON object — no markdown, explanation, or extra text.
#     """
#     response_text = call_groq_api(prompt, temperature=0.2)
#     return safe_extract_json(response_text)

# def refine_resume(info, job_description):
#     prompt = f"""
#     You are an AI resume assistant. Based on the following job description and resume (in JSON), refine and tailor the resume to better fit the role.

#     ✅ Add any relevant skills or projects if they’re missing.
#     ✅ Include a concise "aboutMe" section summarizing the candidate.
#     ✅ Output must be a single valid JSON object only — no extra text, no markdown, no explanation.

#     === Job Description ===
#     {job_description}

#     === Resume JSON ===
#     {json.dumps(info, indent=2)}
#     """
#     response_text = call_groq_api(prompt, temperature=0.3)
#     return safe_extract_json(response_text)

# def generate_cover_letter(info, job_description):
#     prompt = f"""
#     Generate a concise and professional cover letter based on the resume and job description below.

#     === Job Description ===
#     {job_description}

#     === Resume JSON ===
#     {json.dumps(info, indent=2)}

#     Output the letter in plain text with no JSON or markdown formatting.
#     """
#     return call_groq_api(prompt, temperature=0.7)

# def render_latex_code(resume_data):
#     resume_data.setdefault("education", [])
#     resume_data.setdefault("workExperience", [])
#     resume_data.setdefault("projects", [])
#     resume_data.setdefault("skills", [])
#     resume_data.setdefault("certifications", [])
#     resume_data.setdefault("achievements", [])

#     template_dir = os.path.join(os.path.dirname(__file__), "templates")
#     env = Environment(loader=FileSystemLoader(template_dir))
#     template = env.get_template("resume.tex")
#     return template.render(**resume_data)

# # === STREAMLIT UI === #
# st.set_page_config(page_title="Resume & Cover Letter Generator", layout="centered")
# st.title("📄 Smart Resume & Cover Letter Generator")

# uploaded_file = st.file_uploader("Upload your resume (PDF or JSON)", type=["pdf", "json"])
# job_description = st.text_area("Paste the Job Description", height=200)

# if uploaded_file:
#     if uploaded_file.type == "application/pdf":
#         text = extract_text_from_pdf(uploaded_file)
#         resume_info = extract_resume_info(text)
#     else:
#         resume_info = json.load(uploaded_file)

#     if resume_info:
#         st.success("✅ Resume data extracted successfully!")
#         st.subheader("📋 Extracted Resume Info")
#         st.json(resume_info)
#     else:
#         st.error("Failed to extract valid JSON. Check the API response.")
#         st.stop()

#     if job_description:
#         with st.spinner("Refining resume for job description..."):
#             resume_info = refine_resume(resume_info, job_description)
#         st.success("✨ Resume tailored to job description!")

#     if st.button("Generate Cover Letter"):
#         if not job_description:
#             st.warning("Please paste the job description to generate a tailored cover letter.")
#         else:
#             with st.spinner("Generating cover letter..."):
#                 letter = generate_cover_letter(resume_info, job_description)
#             st.subheader("✉️ Generated Cover Letter")
#             st.text_area("Cover Letter", letter, height=300)

#     if st.button("Show LaTeX Code"):
#         with st.spinner("Rendering LaTeX code..."):
#             latex_code = render_latex_code(resume_info)
#             st.subheader("📚 LaTeX Code")
#             st.code(latex_code, language="latex")

#     if st.button("🔍 Analyze ATS Similarity"):
#         with st.spinner("Computing AI similarity score..."):
#             refined_resume_text = json.dumps(resume_info)
#             combined_score = combined_similarity(refined_resume_text, job_description)

#             st.subheader("🤖 Combined AI-Based ATS Similarity Score")
#             st.metric("🔬 Overall Similarity Score", f"{combined_score:.2f}")


import streamlit as st
import json
import pdfplumber
import os
from jinja2 import Environment, FileSystemLoader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import litellm

# === CONFIG === #
st_model = SentenceTransformer('all-MiniLM-L6-v2')
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "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")
PERPLEXITY_API_BASE = "https://api.perplexity.ai"
PERPLEXITY_MODEL = "perplexity/sonar-reasoning-pro"  # ✅ Important: provider/model format

def call_perplexity(prompt, temperature=0.3):
    try:
        response = litellm.completion(
            model=PERPLEXITY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_key=PERPLEXITY_API_KEY,
            api_base=PERPLEXITY_API_BASE,
            temperature=temperature
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"❌ Perplexity API Error: {e}")
        return ""

# === SIMILARITY FUNCTIONS === #
def embedding_similarity(doc1: str, doc2: str) -> float:
    embeddings = st_model.encode([doc1, doc2], convert_to_tensor=False)
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def jaccard_similarity(doc1: str, doc2: str) -> float:
    vec = CountVectorizer().fit_transform([doc1, doc2])
    vec = vec.toarray()
    intersection = np.minimum(vec[0], vec[1]).sum()
    union = np.maximum(vec[0], vec[1]).sum()
    return intersection / union if union != 0 else 0.0

def combined_similarity(doc1: str, doc2: str) -> float:
    emb_score = embedding_similarity(doc1, doc2)
    jac_score = jaccard_similarity(doc1, doc2)
    return round((emb_score + jac_score) / 2, 4)

# === UTILITIES === #
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

def extract_resume_info(text):
    prompt = f"""
    Extract structured resume information from the following raw resume text. Use strong, ATS-optimized formatting:
    - Format output as clean, valid JSON.
    - Extract: personal information(name, phone, email, GitHub, LinkedIn), work_experience, education, skills, certifications, projects, achievements.
    - Use action verbs and quantifiable achievements when possible.
    - Keep section headers professional.

    === RESUME TEXT ===
    {text}
    """
    response_text = call_perplexity(prompt, temperature=0.2)
    return safe_extract_json(response_text)

def refine_resume(info, job_description):
    prompt = f"""
    You are an AI Resume Optimizer. Based on the job description and the candidate's resume (in JSON), rewrite and enhance the resume:
    - Emphasize skills and keywords from the job description.
    - Use measurable results and clear action verbs.
    - Improve structure for ATS readability.
    - Add a professional 'aboutMe' summary (concise, 2-3 lines).
    - Output as VALID JSON (no markdown, no extra text).

    === JOB DESCRIPTION ===
    {job_description}

    === RESUME JSON ===
    {json.dumps(info, indent=2)}
    """
    response_text = call_perplexity(prompt, temperature=0.3)
    return safe_extract_json(response_text)

def generate_cover_letter(info, job_description):
    prompt = f"""
    Write a concise, ATS-friendly cover letter tailored to the job description below.
    - Address key requirements in the job.
    - Reference relevant experience from the resume.
    - Maintain a professional and confident tone.
    - Return the content as clean, plain text only.

    === JOB DESCRIPTION ===
    {job_description}

    === RESUME JSON ===
    {json.dumps(info, indent=2)}
    """
    return call_perplexity(prompt, temperature=0.6)

def render_latex_code(resume_data):
    resume_data.setdefault("personal_information", [])
    resume_data.setdefault("Education", [])
    resume_data.setdefault("work_experience", [])
    resume_data.setdefault("projects", [])
    resume_data.setdefault("skills", {
        "programming_languages": [],
        "scripting_languages": [],
        "databases": [],
        "tools": []
    })
    resume_data.setdefault("certifications", [])
    resume_data.setdefault("achievements", [])

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("resume.tex")
    return template.render(**resume_data)

# === STREAMLIT UI === #
st.set_page_config(page_title="Resume & Cover Letter Generator", layout="centered")
st.title("Smart Resume & Cover Letter Generator")

uploaded_file = st.file_uploader("Upload your resume (PDF or JSON)", type=["pdf", "json"])
job_description = st.text_area("Paste the Job Description", height=200)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
        resume_info = extract_resume_info(text)
    else:
        resume_info = json.load(uploaded_file)

    if resume_info:
        st.success("Resume data extracted successfully!")
        st.subheader("Extracted Resume Info")
        st.json(resume_info)
    else:
        st.error("Failed to extract valid JSON. Check the API response.")
        st.stop()

    if job_description:
        with st.spinner("Refining resume for job description..."):
            resume_info = refine_resume(resume_info, job_description)
        st.success("\u2728 Resume tailored to job description!")

    if st.button("Generate Cover Letter"):
        if not job_description:
            st.warning("Please paste the job description to generate a tailored cover letter.")
        else:
            with st.spinner("Generating cover letter..."):
                letter = generate_cover_letter(resume_info, job_description)
            st.subheader("Generated Cover Letter")
            st.text_area("Cover Letter", letter, height=300)

    if st.button("Show LaTeX Code"):
        with st.spinner("Rendering LaTeX code..."):
            latex_code = render_latex_code(resume_info)
            st.subheader("LaTeX Code")
            st.code(latex_code, language="latex")

    if st.button("Analyze ATS Similarity"):
        with st.spinner("Computing AI similarity score..."):
            refined_resume_text = json.dumps(resume_info)
            combined_score = combined_similarity(refined_resume_text, job_description)

            st.subheader("Combined AI-Based ATS Similarity Score")
            st.metric("Overall Similarity Score", f"{combined_score:.2f*100}")
