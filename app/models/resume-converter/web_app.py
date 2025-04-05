import os
import json
import shutil
import zipfile
import base64

from zlm import AutoApplyModel
from zlm.utils.utils import read_file
from zlm.utils.metrics import jaccard_similarity, overlap_coefficient, cosine_similarity
from zlm.variables import LLM_MAPPING


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

    # Clean previous output
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("uploads", exist_ok=True)

    try:
        downloads_dir = os.path.abspath("output")
        resume_llm = AutoApplyModel(api_key=api_key, provider=provider, model=model, downloads_dir=downloads_dir)

        print("[INFO] Extracting user data from resume...")
        user_data = resume_llm.user_data_extraction(input_file_path, is_st=False)
        print("[USER DATA]", user_data)

        if user_data is None:
            print("[ERROR] Could not extract user data.")
            return

        print("[INFO] Extracting job details...")
        if jd_url:
            job_details, jd_path = resume_llm.job_details_extraction(url=jd_url, is_st=False)
        else:
            job_details, jd_path = resume_llm.job_details_extraction(job_site_content=jd_text, is_st=False)

        print("[JOB DETAILS]", job_details)

        if job_details is None:
            print("[ERROR] Could not extract job details.")
            return

        if get_resume:
            print("[INFO] Generating Resume...")
            resume_path, resume_details = resume_llm.resume_builder(job_details, user_data, is_st=False)
            print(f"[RESUME GENERATED] -> {resume_path}")

            print("[INFO] Calculating resume metrics...")
            for metric in ['overlap_coefficient', 'cosine_similarity']:
                fn = globals()[metric]
                user_score = fn(json.dumps(resume_details), json.dumps(user_data))
                job_alignment_score = fn(json.dumps(resume_details), json.dumps(job_details))
                job_match_score = fn(json.dumps(user_data), json.dumps(job_details))

                print(f"[METRIC: {metric}]")
                print(f"  - User Personalization: {user_score:.3f}")
                print(f"  - Job Alignment: {job_alignment_score:.3f}")
                print(f"  - Job Match: {job_match_score:.3f}")

        if get_cover_letter:
            print("[INFO] Generating Cover Letter...")
            cv_details, cv_path = resume_llm.cover_letter_generator(job_details, user_data, is_st=False)
            print(f"[COVER LETTER GENERATED] -> {cv_path}")
            print("[COVER LETTER CONTENT]\n", cv_details)

        print("[SUCCESS] ✅ Done generating documents.")

    except Exception as e:
        print(f"[ERROR] An exception occurred: {e}")


# Example usage:
if __name__ == "__main__":
    api_key = "your-api-key"
    provider = "OpenAI"
    model = "gpt-4"
    file_path = "uploads/sample_resume.pdf"
    job_text = "We are looking for a Python developer with experience in FastAPI and AI..."
    generate_resume(api_key, provider, model, input_file_path=file_path, jd_text=job_text, get_resume=True, get_cover_letter=True)
