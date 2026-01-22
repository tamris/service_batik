import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def initialize_rag(folder_path="dataset", persist_directory="db_chroma"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # 1. CEK: Jika folder database sudah ada, langsung load saja (Sangat Cepat!)
    if os.path.exists(persist_directory):
        print("--- Memuat RAG dari Database Lokal (Disk) ---")
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # 2. Jika belum ada, baru baca PDF (Hanya jalan sekali selamanya)
    print("--- Membuat Database RAG Baru dari PDF ---")
    all_text = ""
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(folder_path, filename)
                doc = fitz.open(file_path)
                for page in doc:
                    all_text += page.get_text("text") + "\n"
    
    if not all_text: return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(all_text)
    
    # Simpan ke folder db_chroma
    vector_db = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings, 
        persist_directory=persist_directory
    )
    return vector_db