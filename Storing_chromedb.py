import chromadb
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import pandas as pd

# Initialize ChromaDB (Persistent Storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Using Hugging Face Embeddings 
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load and store resumes
df_resumes = pd.read_csv('AI-Resume\\cleaned_resume_dataset.csv')
documents_resumes = [
    Document(page_content=row["cleaned_resume"], metadata={"category": row["Category"]})
    for _, row in df_resumes.iterrows()
]

# Load and store projects
csv_file = "AI-Resume\\project_list.csv"  # Update path if needed
df_projects = pd.read_csv(csv_file)
documents_projects = [
    Document(page_content=row["Project Description"], metadata={"title": row["Project Title"]})
    for _, row in df_projects.iterrows()
]

# Combine both document lists
documents = documents_resumes + documents_projects

# Create & Store in Chroma
vectorstore = Chroma.from_documents(documents, embedding_function, client=chroma_client)

print("Resumes and project descriptions stored in ChromaDB successfully!")
