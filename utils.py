'''
-----------------------------------------------------------------------
File: utils.py
Creation Time: Dec 6th 2023, 7:09 pm
Author: Saurabh Zinjad
Developer Email: zinjadsaurabh1997@gmail.com
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus
-----------------------------------------------------------------------
'''

import os
import re
import time
import json
import base64
import platform
import subprocess
import streamlit as st
import streamlit.components.v1 as components
from fpdf import FPDF
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
from transformers import pipeline

OS_SYSTEM = platform.system().lower()

def write_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(data)



def read_file(file_path, mode="r"):
    with open(file_path, mode) as file:
        file_contents = file.read()
    return file_contents

def write_json(file_path, data):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)

def read_json(file_path: str):
    with open(file_path) as json_file:
        return json.load(json_file)

def job_doc_name(job_details: dict, output_dir: str = "output", type: str = ""):
    company_name = clean_string(job_details["company_name"])
    job_title = clean_string(job_details["job_title"])[:15]
    doc_name = "_".join([company_name, job_title])
    doc_dir = os.path.join(output_dir, company_name)
    os.makedirs(doc_dir, exist_ok=True)

    if type == "jd":
        return os.path.join(doc_dir, f"{doc_name}_JD.json")
    elif type == "resume":
        return os.path.join(doc_dir, f"{doc_name}_resume.json")
    elif type == "cv":
        return os.path.join(doc_dir, f"{doc_name}_cv.txt")
    else:
        return os.path.join(doc_dir, f"{doc_name}_")

def clean_string(text: str):
    text = text.title().replace(" ", "").strip()
    text = re.sub(r"[^a-zA-Z0-9]+", "", text)
    return text

def open_file(file: str):
    if OS_SYSTEM == "darwin":  # macOS
        os.system(f"open {file}")
    elif OS_SYSTEM == "linux":
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print("Error: xdg-open command not found. Please install xdg-utils.")
    elif OS_SYSTEM == "windows":
        try:
            os.startfile(file)
        except AttributeError:
            print("Error: os.startfile is not available on this platform.")
    else:
        # Default fallback for other systems
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print(f"Error: xdg-open command not found. Please install xdg-utils. Alternatively, open the file manually.")

def save_log(content: any, file_name: str):
    timestamp = int(datetime.timestamp(datetime.now()))
    file_path = f"logs/{file_name}_{timestamp}.txt"
    write_file(file_path, content)

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        func_run_log = f"Function {func.__name__} took {execution_time:.4f} seconds to execute"
        print(func_run_log)
        return result
    return wrapper

def text_to_pdf(text: str, file_path: str):
    pdf = MarkdownPdf(toc_level=2)
    encoded_text = text.encode('utf-8').decode('latin-1')
    pdf.add_section(Section(encoded_text), user_css="body {font-size: 12pt; font-family: Calibri; text-align: justify;}")
    pdf.meta["title"] = "Cover Letter"
    pdf.meta["author"] = "Saurabh Zinjad"
    pdf.save(file_path)

def download_pdf(pdf_path: str):
    bytes_data = read_file(pdf_path, "rb")
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:application/pdf;base64,{base64_pdf}" download="{os.path.basename(pdf_path)}">')[0].click().remove();
    </script>
    </head>
    </html>
    """
    components.html(
        dl_link,
        height=0,
    )

from pdf2image import convert_from_path

def display_pdf(file, type="pdf"):
    if type == 'image':
        pages = convert_from_path(file)
        for page in pages:
            st.image(page, use_column_width=True)

    if type == "pdf":
        bytes_data = read_file(file, "rb")
        try:
            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            base64_pdf = base64.b64encode(bytes_data)

        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" style="width:100%; height:100vh;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

def save_latex_as_pdf(tex_file_path: str, dst_path: str):
    try:
        prev_loc = os.getcwd()
        os.chdir(os.path.dirname(tex_file_path))
        try:
            result = subprocess.run(
                ["pdflatex", tex_file_path, "&>/dev/null"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print("Pdflatex failed to convert tex file to pdf.")
            print(e)

        os.chdir(prev_loc)
        resulted_pdf_path = tex_file_path.replace(".tex", ".pdf")
        dst_tex_path = dst_path.replace(".pdf", ".tex")

        os.rename(resulted_pdf_path, dst_path)
        os.rename(tex_file_path, dst_tex_path)

        if result.returncode != 0:
            print("Exit-code not 0, check result!")
        try:
            pass
        except Exception as e:
            print("Unable to open the PDF file.")
            st.write("Unable to open the PDF file.")

        filename_without_ext = os.path.basename(tex_file_path).split(".")[0]
        unnessary_files = [
            file
            for file in os.listdir(os.path.dirname(os.path.realpath(tex_file_path)))
            if file.startswith(filename_without_ext)
        ]

        for file in unnessary_files:
            file_path = os.path.join(os.path.dirname(tex_file_path), file)
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(e)
        return None

def get_default_download_folder():
    downlaod_folder_path = os.path.join(str(Path.home()), "Downloads", "JobLLM_Resume_CV")
    print(f"downlaod_folder_path: {downlaod_folder_path}")
    os.makedirs(downlaod_folder_path, exist_ok=True)
    return downlaod_folder_path

def parse_json_markdown(json_string: str) -> dict:
    try:
        if json_string[3:13].lower() == "typescript":
            json_string = json_string.replace(json_string[3:13], "",1)
        
        if 'JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA' in json_string:
            json_string = json_string.replace("JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA", "",1)
        
        if json_string[3:7].lower() == "json":
            json_string = json_string.replace(json_string[3:7], "",1)
    
        parser = JsonOutputParser()
        parsed = parser.parse(json_string)

        return parsed
    except Exception as e:
        print(e)
        return None

def get_prompt(system_prompt_path: str) -> str:
    with open(system_prompt_path, encoding="utf-8") as file:
        return file.read().strip() + "\n"

def key_value_chunking(data, prefix=""):
    chunks = []
    stop_needed = lambda value: '.' if not isinstance(value, (str, int, float, bool, list)) else ''
    
    if isinstance(data, dict):
        for key, value in data.items():
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{prefix}{key}{stop_needed(value)}"))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{prefix}_{index}{stop_needed(value)}"))
    else:
        if data is not None:
            chunks.append(f"{prefix}: {data}")
    
    return chunks

class DeepSeekModel:
    def __init__(self, api_key, system_prompt):
        self.system_prompt = system_prompt
        self.client = pipeline("text-generation", model="deepseek-ai/DeepSeek-V3-0324", api_key=api_key, trust_remote_code=True)
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False):
        user_prompt = f"{self.system_prompt}\n{prompt}"
        chunk_size = 1024
        responses = []

        try:
            for i in range(0, len(user_prompt), chunk_size):
                chunk = user_prompt[i:i + chunk_size]
                completion = self.client(chunk, max_length=4000 if expecting_longer_output else None, return_full_text=False)
                content = completion[0]['generated_text'].strip()
                responses.append(content)
            
            full_response = " ".join(responses)
            
            if need_json_output:
                return parse_json_markdown(full_response)
            else:
                return full_response
        
        except Exception as e:
            print(e)
            st.error(f"Error in Hugging Face API, {e}")
            st.markdown("<h3 style='text-align: center;'>Please try again! Check the log in the dropdown for more details.</h3>", unsafe_allow_html=True)
    
    def get_embedding(self, text, model="deepseek-ai/DeepSeek-V3-0324", task_type="retrieval_document"):
        try:
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input = [text], model=model, trust_remote_code=True).data[0].embedding
        except Exception as e:
            print(e)