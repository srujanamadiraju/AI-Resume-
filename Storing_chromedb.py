import chromadb
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import chromadb
#from sentence_transformers import SentenceTransformer
import pandas as pd 
import numpy as np 

# Convert resumes into LangChain Document format

df = pd.read_csv('AI-Resume-/cleaned_resume_dataset.csv')

documents = [
    Document(page_content=row["cleaned_resume"], metadata={"category": row["Category"]})
    for _, row in df.iterrows()
]

# Initialize ChromaDB (Persistent Storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# ✅ Using Hugging Face Embeddings 
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create & Store in Chroma
vectorstore = Chroma.from_documents(documents, embedding_function, client=chroma_client)

print("Resumes stored in ChromaDB successfully! ✅")
