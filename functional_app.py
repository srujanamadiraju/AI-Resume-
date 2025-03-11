from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import os
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
from summarize import summarize_jdresume
from resume_sim import resume_checkup
from chatbot import get_readychain
from bert_code import get_your_match, get_similarity_perc

# Flask app initialization
app = Flask(__name__)

# Initialize ChromaDB for persistent storage
chroma_client = chromadb.PersistentClient(path="chroma_db")  
collection = chroma_client.get_or_create_collection(name="resumes")

# Sentence Transformer Embedding Model
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Ensure the Data folder exists
os.makedirs("Data", exist_ok=True)

# Chat history
chat_list = []
greeted = False  # Flag to ensure greeting only happens once

def extract_text_from_resume(resume_file):
    """Extract text from PDF or Image Resume."""
    extracted_text = ""
    file_extension = os.path.splitext(resume_file.filename)[-1].lower()

    if file_extension == ".pdf":
        pdf_reader = PdfReader(resume_file)
        extracted_text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    elif file_extension in [".png", ".jpg", ".jpeg"]:
        image = Image.open(resume_file)
        extracted_text = pytesseract.image_to_string(image)
    
    return extracted_text.strip()

@app.route('/')
def index():
    return render_template('chat4.html')

@app.route('/upload', methods=['POST'])
def upload():
    job_description = request.form.get("job_description")
    resume_file = request.files.get("resume")

    response = {}

    # Store Job Description in ChromaDB
    if job_description:
        job_desc_embedding = embedding_model([job_description])[0]
        collection.upsert(documents=[job_description], embeddings=[job_desc_embedding], ids=["job_description"])
        response["jd_status"] = "Job description stored successfully."

    # Store Resume in ChromaDB
    if resume_file:
        extracted_text = extract_text_from_resume(resume_file)
        if extracted_text:
            resume_id = f"resume_{len(collection.get()['ids']) + 1}"  # Unique ID
            resume_embedding = embedding_model([extracted_text])[0]

            metadata = {
                "filename": resume_file.filename,
                "uploaded_at": str(datetime.now())
            }

            collection.upsert(documents=[extracted_text], embeddings=[resume_embedding], ids=[resume_id], metadatas=[metadata])
            response["resume_status"] = f"Resume {resume_file.filename} stored successfully."
        else:
            response["resume_status"] = "Failed to extract text from the resume."

    return jsonify(response)

@app.route('/get', methods=['POST'])
def chat():
    global greeted
    user_message = request.form.get("msg").strip().lower()
    print("User message received:", user_message)

    # Common greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

    if user_message in greetings:
        if not greeted:
            greeted = True
            return jsonify({"response": "Hello! How can I assist you today?"})
        else:
            return jsonify({"response": "Hey again! How can I help you?"})

    # Retrieve job description
    job_desc_data = collection.get(ids=["job_description"])
    if not job_desc_data['documents']:
        return jsonify({"response": "No job description found. Please upload one first."})
    
    job_description = job_desc_data["documents"][0]

    total_resumes = len(collection.get()['ids']) - 1  # Exclude job description
    n_results = min(5, total_resumes) 

    # Retrieve top resumes dynamically
    retrieved_resumes = collection.query(query_texts=[job_description], n_results=n_results)
    retrieved_texts = retrieved_resumes["documents"]

    if not retrieved_texts:
        return jsonify({"response": "No matching resumes found. Please upload a resume."})

    # Flatten list and join
    resume_summary = "\n".join([" ".join(text) if isinstance(text, list) else text for text in retrieved_texts])

    # Get keywords
    resume_kw = get_your_match(input_path=os.path.join("Data", "jd.txt"))
    jd_kw = get_your_match(input_path=os.path.join("Data", "resume.txt"))

    # Get match percentage
    percentage = get_similarity_perc(resume_keywords=resume_kw, jd_keywords=jd_kw)

    # Generate response with concise output
    system_msg, _ = resume_checkup(resume_summary=resume_summary, jd_summary=job_description, perc=percentage)
    
    concise_prompt = f"Summarize in 2-3 sentences: {system_msg}"  # Force concise LLM response
    chain = get_readychain(system_msg=concise_prompt)

    ai_msg = chain.invoke({"messages": chat_list})

    chat_list.append({"role": "assistant", "content": ai_msg.content})

    return jsonify({"response": ai_msg.content if hasattr(ai_msg, 'content') else str(ai_msg)})

if __name__ == '__main__':
    app.run(debug=True)
