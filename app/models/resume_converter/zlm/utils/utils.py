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
# import streamlit as st
import streamlit.components.v1 as components
from fpdf import FPDF
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
OS_SYSTEM = platform.system().lower()



def write_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(data) # writing latex data to NotSpecified_MachineLearning_resume.tex


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
        # if 'is_st' in kwargs and kwargs['is_st']:
        #     st.write(func_run_log)

        return result

    return wrapper


def text_to_pdf(text: str, file_path: str):
    """Converts the given text to a PDF and saves it to the specified file path.

    Args:
        text (str): The text to be converted to PDF.
        file_path (str): The file path where the PDF will be saved.
    """
    # from mistletoe import markdown
    # pdf = FPDF()
    # pdf.add_page()
    # pdf.set_font("Arial", size=11)
    # # Encode the text explicitly using 'latin-1' encoding
    # encoded_text = text.encode('utf-8').decode('latin-1')
    # html_text = markdown(encoded_text)
    # pdf.write_html(html_text)
    # # pdf.multi_cell(0, 5, txt=encoded_text)
    # pdf.output(file_path)

    pdf = MarkdownPdf(toc_level=2)
    # pdf.set_font("Arial", size=11)
    # Encode the text explicitly using 'latin-1' encoding
    encoded_text = text.encode('utf-8').decode('latin-1')
    pdf.add_section(Section(encoded_text), user_css="body {font-size: 12pt; font-family: Calibri; text-align: justify;}")
    pdf.meta["title"] = "Cover Letter"
    pdf.meta["author"] = "Saurabh Zinjad"
    pdf.save(file_path)


    # try:
    #     open_file(file_path)
    # except Exception as e:
    #     print("Unable to open the PDF file.")

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
    # with open(pdf_path, "rb") as f:
    #     pdf_bytes = f.read()

    # st.download_button(label="Download Resume ⬇",
    #                     data=pdf_bytes,
    #                     file_name=os.path.basename(pdf_path),
    #                     mime="application/pdf")
    # pass

from pdf2image import convert_from_path

def display_pdf(file, type="pdf"):
    if type == 'image':
        # Store Pdf with convert_from_path function
        pages = convert_from_path(file)
        # for page in pages:
        #     st.image(page, use_column_width=True)

    if type == "pdf":
        # Read file as bytes:
        bytes_data = read_file(file, "rb")

        # Convert to utf-8
        try:
            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            base64_pdf = base64.b64encode(bytes_data)

        # Iframe Embedding of PDF in HTML
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" style="width:100%; height:100vh;"></iframe>'
        
        # # Embedding PDF in HTML
        # pdf_display =  f"""<embed
        # class="pdfobject"
        # type="application/pdf"
        # title="Embedded PDF"
        # src="data:application/pdf;base64,{base64_pdf}"
        # style="overflow: auto; width: 100%; height: 100vh">"""

        # Display file
        # st.markdown(pdf_display, unsafe_allow_html=True)

def save_latex_as_pdf(tex_file_path: str, dst_path: str):
    try:
        # Call pdflatex to convert LaTeX to PDF
        prev_loc = os.getcwd()
        os.chdir(os.path.dirname(tex_file_path))
        try:
            print("hi")
            print(tex_file_path)
            result = subprocess.run(
                ["pdflatex", tex_file_path, "&>/dev/null"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print("Pdflatex failed to convert tex file to pdf.")
            print(e)

        print("over")
        os.chdir(prev_loc)
        resulted_pdf_path = tex_file_path.replace(".tex", ".pdf")
        dst_tex_path = dst_path.replace(".pdf", ".tex")

        os.rename(resulted_pdf_path, dst_path)
        os.rename(tex_file_path, dst_tex_path)


        if result.returncode != 0:
            print("Exit-code not 0, check result!")
        try:
            pass
            # open_file(dst_path)
        except Exception as e:
            print("Unable to open the PDF file.")

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

# def save_latex_as_pdf(tex_file_path: str, dst_path: str):
#     try:
#         # Check if pdflatex is installed
#         pdflatex_installed = False
#         try:
#             subprocess.run(["pdflatex", "--version"], 
#                           stdout=subprocess.PIPE, 
#                           stderr=subprocess.PIPE, 
#                           check=False)
#             pdflatex_installed = True
#         except FileNotFoundError:
#             print("pdflatex not found. Attempting to install minimal LaTeX...")
            
#             # Install minimal LaTeX based on the operating system
#             import platform
#             system = platform.system()
            
#             if system == "Windows":
#                 try:
#                     # Try to install TinyTeX
#                     print("Installing TinyTeX (minimal LaTeX distribution)...")
#                     subprocess.run([
#                         "powershell", 
#                         "-Command", 
#                         "iwr -outf install-windows.bat https://yihui.org/tinytex/install-bin-windows.bat; .\install-windows.bat"
#                     ], check=True)
                    
#                     # Add TinyTeX to PATH for current process
#                     import os
#                     home_dir = os.path.expanduser("~")
#                     os.environ["PATH"] += os.pathsep + os.path.join(home_dir, "AppData", "Roaming", "TinyTeX", "bin", "win32")
#                     pdflatex_installed = True
#                     print("TinyTeX installed successfully!")
#                 except Exception as e:
#                     print(f"Failed to install TinyTeX: {e}")
                    
#             elif system == "Linux":
#                 try:
#                     # Try to install texlive-base on Linux
#                     print("Installing texlive-base...")
#                     subprocess.run(["apt-get", "update", "-y"], check=True)
#                     subprocess.run(["apt-get", "install", "-y", "texlive-base"], check=True)
#                     pdflatex_installed = True
#                     print("texlive-base installed successfully!")
#                 except Exception as e:
#                     print(f"Failed to install texlive-base: {e}")
                    
#             elif system == "Darwin":  # macOS
#                 try:
#                     # Try to install BasicTeX on macOS using Homebrew
#                     print("Installing BasicTeX via Homebrew...")
#                     subprocess.run(["brew", "install", "--cask", "basictex"], check=True)
#                     # Add to PATH for current process
#                     os.environ["PATH"] += os.pathsep + "/Library/TeX/texbin"
#                     pdflatex_installed = True
#                     print("BasicTeX installed successfully!")
#                 except Exception as e:
#                     print(f"Failed to install BasicTeX: {e}")
            
#             # Verify installation
#             try:
#                 subprocess.run(["pdflatex", "--version"], 
#                               stdout=subprocess.PIPE, 
#                               stderr=subprocess.PIPE, 
#                               check=False)
#                 pdflatex_installed = True
#             except FileNotFoundError:
#                 print("LaTeX installation was not successful.")
        
#         if not pdflatex_installed:
#             print("Could not install LaTeX. PDF generation will not be possible.")
#             return None
        
#         # Now proceed with PDF generation as normal
#         print(f"Converting LaTeX file: {tex_file_path}")
#         prev_loc = os.getcwd()
#         tex_dir = os.path.dirname(tex_file_path)
#         tex_filename = os.path.basename(tex_file_path)
        
#         os.chdir(tex_dir)
#         try:
#             # Run pdflatex with just the filename (not the full path)
#             # and without shell redirection which doesn't work directly in subprocess
#             result = subprocess.run(
#                 ["pdflatex", "-interaction=nonstopmode", tex_filename],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True,
#                 check=False
#             )
            
#             if result.returncode != 0:
#                 print(f"pdflatex returned non-zero exit code: {result.returncode}")
#                 # Print some of the output for debugging
#                 if result.stderr:
#                     print(f"stderr: {result.stderr}")
#                 if result.stdout:
#                     print(f"Last 500 chars of stdout: {result.stdout[-500:]}")
#         except Exception as e:
#             print(f"pdflatex execution failed: {e}")
#             os.chdir(prev_loc)
#             return None

#         os.chdir(prev_loc)
        
#         # Get paths for the generated files
#         filename_without_ext = os.path.splitext(tex_filename)[0]
#         resulted_pdf_path = os.path.join(tex_dir, filename_without_ext + ".pdf")
#         dst_tex_path = dst_path.replace(".pdf", ".tex")
        
#         # Check if PDF was created
#         if not os.path.exists(resulted_pdf_path):
#             print(f"PDF file was not created: {resulted_pdf_path}")
#             return None
            
#         # Create destination directory if it doesn't exist
#         dst_dir = os.path.dirname(dst_path)
#         if not os.path.exists(dst_dir):
#             os.makedirs(dst_dir, exist_ok=True)
        
#         # Copy files instead of renaming to avoid cross-device link errors
#         import shutil
#         shutil.copy2(resulted_pdf_path, dst_path)
#         shutil.copy2(tex_file_path, dst_tex_path)
        
#         print(f"PDF successfully created at: {dst_path}")

#         # Clean up temporary files
#         temp_extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk']
#         for ext in temp_extensions:
#             temp_file = os.path.join(tex_dir, filename_without_ext + ext)
#             if os.path.exists(temp_file):
#                 os.remove(temp_file)
                
#         return dst_path
        
#     except Exception as e:
#         print(f"Error in save_latex_as_pdf: {e}")
#         import traceback
#         traceback.print_exc()
#         return None 


def get_default_download_folder():
    """Get the default download folder for the current operating system."""
    downlaod_folder_path = os.path.join(str(Path.home()), "Downloads", "JobLLM_Resume_CV")
    print(f"downlaod_folder_path: {downlaod_folder_path}")
    os.makedirs(downlaod_folder_path, exist_ok=True)
    return downlaod_folder_path

def parse_json_markdown(json_string: str) -> dict:
    try:
        # Try to find JSON string within first and last triple backticks
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
        """
        Reads the content of the file at the given system_prompt_path and returns it as a string.

        Args:
            system_prompt_path (str): The path to the system prompt file.

        Returns:
            str: The content of the file as a string.
        """
        with open(system_prompt_path, encoding="utf-8") as file:
            return file.read().strip() + "\n"


def key_value_chunking(data, prefix=""):
    """Chunk a dictionary or list into key-value pairs.

    Args:
        data (dict or list): The data to chunk.
        prefix (str, optional): The prefix to use for the keys. Defaults to "".

    Returns:
        A list of strings representing the chunked key-value pairs.
    """
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