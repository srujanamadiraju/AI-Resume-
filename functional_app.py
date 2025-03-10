'''
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract  # For OCR
import os
from dotenv import load_dotenv
from summarize import summarize_jdresume
from resume_sim import resume_checkup
from chatbot import get_readychain
from bert_code import get_your_match, get_similarity_perc

# ChromaDB Imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Ensure the Data folder exists
os.makedirs("Data", exist_ok=True)

# Initialize ChromaDB
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Example model
vector_store = Chroma(persist_directory="chroma_db", embedding_function=embedding_model)

# Function to retrieve latest job description from ChromaDB
def get_current_job_description():
    """
    Retrieve the latest job description stored in ChromaDB.
    """
    docs = vector_store.similarity_search("job description", k=1)  # Get the most relevant JD
    return docs[0].page_content if docs else "No job description found."

# Function to load previous chat history from ChromaDB
def load_chat_history():
    history = []
    docs = vector_store.similarity_search("previous conversation", k=10)
    for doc in docs:
        history.append({"role": "user", "content": doc.page_content})
    return history

# Load existing chat history
chat_list = load_chat_history()

def format_chatbot_response(response_text):
    """
    Format the chatbot's response to create headers from bold text (indicated by **).
    """
    formatted_text = ""
    
    # Split the response into lines or sections (assuming ** indicates a header).
    sections = response_text.split("\n")
    
    for section in sections:
        if "" in section:
            header = section.replace("", "").strip()
            formatted_text += f'<h4 style="color: #18191a; font-weight: bold; font-size: 1rem;">{header}</h4>'
        else:
            formatted_text += f'<p>{section.strip()}</p>'
    
    return formatted_text

@app.route('/')
def index():
    return render_template('chat4.html')

@app.route('/upload', methods=['POST'])
def upload():
    job_description = request.form.get("job_description")
    resume_file = request.files.get("resume")

    response = {}

    # Define file paths
    jd_file_path = os.path.join("Data", "jd.txt")
    resume_file_path = os.path.join("Data", "resume.txt")

    # 🛠 Delete existing files before writing new ones
    for file_path in [jd_file_path, resume_file_path]:
        if os.path.exists(file_path):
            os.remove(file_path)  # Delete the file

    # 🔹 Save job description
    if job_description:
        with open(jd_file_path, "w", encoding="utf-8") as jd_file:
            jd_file.write(job_description)
        response["jd_status"] = "Job description saved successfully."

        # 🔹 Store Job Description in ChromaDB
        jd_doc = Document(page_content=job_description, metadata={"type": "job_description"})
        vector_store.add_documents([jd_doc])
        response["jd_chroma_status"] = "Job description stored in ChromaDB."

    # 🔹 Save and process resume
    if resume_file:
        extracted_text = ""
        file_extension = os.path.splitext(resume_file.filename)[-1].lower()

        if file_extension == ".pdf":
            pdf_reader = PdfReader(resume_file)
            extracted_text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif file_extension in [".png", ".jpg", ".jpeg"]:
            image = Image.open(resume_file)
            extracted_text = pytesseract.image_to_string(image)

        # 🛠 Write extracted text to a new file
        if extracted_text:
            with open(resume_file_path, "w", encoding="utf-8") as resume_file:
                resume_file.write(extracted_text)
            response["resume_status"] = "Resume processed successfully."
        else:
            response["resume_status"] = "Failed to extract text from the resume."

    return jsonify(response)

@app.route('/get', methods=['POST'])
def chat():
    user_message = request.form.get("msg")
    
    print(user_message)
    
    # 🔹 Fetch the latest Job Description from ChromaDB
    jd_text = get_current_job_description()
    
    # 🔹 Process summaries
    jd_summary = summarize_jdresume(input_text=jd_text)  
    resume_summary = summarize_jdresume(input_path=os.path.join("Data", "resume.txt"))
    
    # 🔹 Extract keywords dynamically
    resume_kw = get_your_match(input_text=jd_text)  
    jd_kw = get_your_match(input_path=os.path.join("Data", "resume.txt"))

    # 🔹 Calculate similarity
    percentage = get_similarity_perc(resume_keywords=resume_kw, jd_keywords=jd_kw)

    system_msg, _ = resume_checkup(
        resume_summary=resume_summary, jd_summary=jd_summary, perc=percentage
    )

    print(chat_list)

    # Append user message and AI response to chat history
    chat_list.append({"role": "assistant", "content": f"Based on the job description and resume we got {percentage} match"})
    chat_list.append({"role": "user", "content": user_message})
    
    chain = get_readychain(system_msg=system_msg)
    ai_msg = chain.invoke({"messages": chat_list})

    print(ai_msg)
    chat_list.append({"role": "assistant", "content": ai_msg.content})

    # Store new conversation in ChromaDB
    new_doc = Document(page_content=ai_msg.content, metadata={"type": "chat"})
    vector_store.add_documents([new_doc])

    return format_chatbot_response(ai_msg.content)

if __name__ == '_main_':
    app.run(debug=True)'
    '''

from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract  # For OCR
import os
from summarize import summarize_jdresume
from resume_sim import resume_checkup
from chatbot import get_readychain
from bert_code import get_your_match, get_similarity_perc

# Flask app initialization
app = Flask(__name__)

# Ensure the Data folder exists
os.makedirs("Data", exist_ok=True)

# Chat history
chat_list = []
greeted = False  # Flag to ensure greeting only happens once

# Directory for storing multiple resumes
os.makedirs("Data/Resumes", exist_ok=True)

def format_chatbot_response(response_text):
    """
    Format the chatbot's response to create headers from bold text (indicated by `**`).
    """
    formatted_text = ""
    
    sections = response_text.split("\n")
    
    for section in sections:
        if "**" in section:
            header = section.replace("**", "").strip()
            formatted_text += f'<h4 style="color: #18191a; font-weight: bold; font-size: 1rem;">{header}</h4>'
        else:
            formatted_text += f'<p>{section.strip()}</p>'
    
    return formatted_text

@app.route('/')
def index():
    return render_template('chat4.html')

@app.route('/upload', methods=['POST'])
def upload():
    job_description = request.form.get("job_description")
    resume_file = request.files.get("resume")

    response = {}

    # Save job description
    if job_description:
        jd_file_path = os.path.join("Data", "jd.txt")
        with open(jd_file_path, "w", encoding="utf8") as jd_file:
            jd_file.write(job_description)
        response["jd_status"] = "Job description saved successfully."

    # Save and process multiple resumes
    if resume_file:
        extracted_text = ""
        file_extension = os.path.splitext(resume_file.filename)[-1].lower()
        resume_filename = f"resume_{len(os.listdir('Data/Resumes')) + 1}.txt"  # Unique filename
        resume_file_path = os.path.join("Data/Resumes", resume_filename)

        if file_extension == ".pdf":
            pdf_reader = PdfReader(resume_file)
            extracted_text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif file_extension in [".png", ".jpg", ".jpeg"]:
            image = Image.open(resume_file)
            extracted_text = pytesseract.image_to_string(image)

        if extracted_text:
            with open(resume_file_path, "w", encoding="utf-8") as resume_txt_file:
                resume_txt_file.write(extracted_text)
            response["resume_status"] = f"Resume {resume_filename} processed successfully."
        else:
            response["resume_status"] = "Failed to extract text from the resume."

    return jsonify(response)

@app.route('/get', methods=['POST'])
def chat():
    global greeted
    user_message = request.form.get("msg").strip().lower()
    print(user_message)

    # Common greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

    if user_message in greetings:
        if not greeted:
            greeted = True
            return format_chatbot_response("Hello! How can I assist you today?")
        else:
            return format_chatbot_response("Hey again! How can I help you?")

    # Proceed with resume analysis only if it's NOT a greeting
    resume_texts = []
    for resume_file in os.listdir("Data/Resumes"):
        resume_path = os.path.join("Data/Resumes", resume_file)
        resume_texts.append(summarize_jdresume(input_path=resume_path))

    jd_summary = summarize_jdresume(input_path=os.path.join("Data", "jd.txt"))

    # Merge resume summaries
    resume_summary = "\n".join(resume_texts)

    # Get keywords
    resume_kw = get_your_match(input_path=os.path.join("Data", "jd.txt"))
    jd_kw = get_your_match(input_path=os.path.join("Data", "resume.txt"))

    # Get match percentage
    percentage = get_similarity_perc(resume_keywords=resume_kw, jd_keywords=jd_kw)

    # Generate response
    system_msg, _ = resume_checkup(resume_summary=resume_summary, jd_summary=jd_summary, perc=percentage)

    chat_list.append({"role": "assistant", "content": f"The resume matches {percentage}% with the job description."})
    chat_list.append({"role": "user", "content": user_message})

    # Pass system message to LLM
    chain = get_readychain(system_msg=system_msg)
    ai_msg = chain.invoke({"messages": chat_list})

    chat_list.append({"role": "assistant", "content": ai_msg.content})

    return format_chatbot_response(ai_msg.content)

if __name__ == '__main__':
    app.run(debug=True)
