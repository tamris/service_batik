import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def initialize_rag(folder_path="dataset"):
    all_text = ""
    try:
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(folder_path, filename)
                    doc = fitz.open(file_path)
                    for page in doc:
                        all_text += page.get_text("text") + "\n"
        
        if not all_text:
            return None

        # Split text menjadi chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_text(all_text)
        
        # Embedding menggunakan HuggingFace
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = Chroma.from_texts(chunks, embedding=embeddings)
        return vector_db
    except Exception as e:
        print(f"Error RAG: {e}")
        return None