import os
import json
import shutil
import zipfile
import base64

import nltk
from nltk.tokenize import word_tokenize
import re

from app.models.resume_converter.zlm import AutoApplyModel
from app.models.resume_converter.zlm.utils.utils import read_file 
from app.models.resume_converter.zlm.utils.metrics import jaccard_similarity, overlap_coefficient, cosine_similarity
from app.models.resume_converter.zlm.variables import LLM_MAPPING

from dotenv import load_dotenv


def encode_tex_file(file_path):
    try:
        current_loc = os.path.dirname(__file__)
        tex_file = file_path.replace('.pdf', '.tex')
        cls_file = os.path.join(current_loc, 'zlm', 'templates', 'resume.cls')
        zip_file_path = file_path.replace('.pdf', '.zip')

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(tex_file, os.path.basename(tex_file))
            zipf.write(cls_file, os.path.basename(cls_file))

        with open(zip_file_path, 'rb') as zip_file:
            encoded_zip = base64.b64encode(zip_file.read()).decode('utf-8')
        return encoded_zip
    except Exception as e:
        print(f"[ERROR] Failed to encode .tex file: {e}")
        return None


def generate_resume(api_key, provider, model, input_file_path, jd_url="", jd_text="", get_resume=True, get_cover_letter=False):
    if not os.path.exists(input_file_path):
        print(f"[ERROR] Input file does not exist: {input_file_path}")
        return

    if not (jd_url or jd_text):
        print("[ERROR] Job description or URL is required.")
        return

    if not api_key and provider.lower() != "ollama":
        print("[ERROR] API key is required for provider:", provider)
        return

    # Clean previous output  ### rmoutput
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("uploads", exist_ok=True)

    try:
        downloads_dir = os.path.abspath("output")
        resume_llm = AutoApplyModel(api_key=api_key, provider=provider, model=model, downloads_dir=downloads_dir)

        print("[INFO] Extracting user data from resume...")
        user_data = resume_llm.user_data_extraction(input_file_path, is_st=False)
        # print("[USER DATA]", user_data)

        if user_data is None:
            print("[ERROR] Could not extract user data.")
            return

        print("[INFO] Extracting job details...")
        if jd_url:
            job_details = resume_llm.job_details_extraction(url=jd_url, is_st=False)
        else:
            job_details = resume_llm.job_details_extraction(job_site_content=jd_text, is_st=False)

        # print("[JOB DETAILS]", job_details)

        if job_details is None:
            print("[ERROR] Could not extract job details.")
            return

        if get_resume:
            print("[INFO] Generating Resume...")
            resume_details , resume_latex = resume_llm.resume_builder(job_details, user_data, is_st=False)
            # print(f"[TEX GENERATED PATH] -> {tex_path}")
            
        metrics_dict = {}
        for metric in ['overlap_coefficient', 'cosine_similarity']:
            try:
                print(f"[INFO] Calculating metric: {metric}")
                if metric == 'overlap_coefficient':
                    user_score = overlap_coefficient(json.dumps(resume_details), json.dumps(user_data))
                    job_alignment_score = overlap_coefficient(json.dumps(resume_details), json.dumps(job_details))
                    job_match_score = overlap_coefficient(json.dumps(user_data), json.dumps(job_details))
                else:
                    fn = globals()[metric]
                    user_score = fn(json.dumps(resume_details), json.dumps(user_data))
                    job_alignment_score = fn(json.dumps(resume_details), json.dumps(job_details))
                    job_match_score = fn(json.dumps(user_data), json.dumps(job_details))

                print(f"[METRIC: {metric}]")
                print(f"  - User Personalization: {user_score:.3f}")
                print(f"  - Job Alignment: {job_alignment_score:.3f}")
                print(f"  - Job Match: {job_match_score:.3f}")
                
                metrics_dict[metric] = {"user_score":user_score,"job_alignment_score":job_alignment_score,"job_match_score":job_match_score}
            except Exception as e:
                print(f"[ERROR] Failed on metric {metric}: {e}")


        if get_cover_letter:
            print("[INFO] Generating Cover Letter...")
            cv_details = resume_llm.cover_letter_generator(job_details, user_data, is_st=False)
            # print(f"[COVER LETTER GENERATED] -> {cv_path}")
            print("[COVER LETTER CONTENT]\n", cv_details)

        print("[SUCCESS] ✅ Done generating documents.")
        
        # resume_cls = read_file(r"models\resume_converter\zlm\templates\resume.cls")
        
        return resume_latex , metrics_dict 

    except Exception as e:
        print(f"[ERROR] An exception occurred: {e}")


def overlap_coefficient(text1, text2):
    
    # Use a simple regex tokenizer as an alternative
    def simple_tokenize(text):
        # Convert to lowercase and split by non-alphanumeric characters
        return re.findall(r'\w+', text.lower())
    
    tokens1 = set(simple_tokenize(text1))
    tokens2 = set(simple_tokenize(text2))
    intersection = tokens1.intersection(tokens2)
    smallest_set_size = min(len(tokens1), len(tokens2)) 
    if smallest_set_size == 0:
        return 0.0
    return len(intersection) / smallest_set_size


# Example usage:
def convert_resume(file_path,job_text):
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")
    print(f"[API_KEY] {api_key}")
    provider = "Perplexity"
    model = "sonar-pro"
    # file_path = r"app\models\resume-converter\uploads\janardhan_resume.pdf"
    # job_text = "We’re hiring a Machine Learning Engineer to build scalable AI solutions for healthcare diagnostics. Responsibilities include model development, deployment, and optimizing real-time performance.Requirements: Proficiency in Python, TensorFlow/PyTorch, and experience with medical imaging datasets."
    cls_path = r"models\resume_converter\zlm\templates\resume.cls"
    resume_cls = read_file(cls_path)
    
    resume_latex , metrics_dict = generate_resume(api_key, provider, model, input_file_path=file_path, jd_text=job_text, get_resume=True, get_cover_letter=False)
    
    # resume_cls = remove_escape_sequences(resume_cls)
    # resume_latex = remove_escape_sequences(resume_latex)
    
    return resume_latex , resume_cls ,  metrics_dict 
