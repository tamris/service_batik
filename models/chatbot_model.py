# models/chatbot_model.py
import google.generativeai as genai
from flask import current_app

class ChatbotModel:
    def __init__(self, vector_db=None):
        # Setting temperature rendah (0.1 - 0.2) agar jawaban fokus pada data, bukan kreativitas
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 512,
        }
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=self.generation_config
        )
        self.vector_db = vector_db

    def ask_ai(self, question):
        context = ""
        if self.vector_db:
            # Ambil lebih banyak potongan teks (k=7) untuk akurasi data
            retriever = self.vector_db.as_retriever(search_kwargs={"k":7})
            docs = retriever.invoke(question)
            context = "\n".join([d.page_content for d in docs])

        # Prompt dengan instruksi "Data-First"
        prompt = f"""
        Kamu adalah TikAI, asisten Sistem Informasi Batik Tegalan.
        
        TUGAS UTAMA:
        - Gunakan **detail spesifik** dari 'KONTEKS DATASET' (seperti nama tokoh, tahun, dan istilah teknis).
        - Jika informasi ada di KONTEKS DATASET, **dilarang** memberikan jawaban umum yang bertele-tele.
        - Langsung ke inti jawaban dalam bentuk poin-poin.
        - Hindari basa-basi "Wah, pertanyaan yang menarik!" agar user cepat mendapat informasi.

        KONTEKS DATASET:
        {context}

        PERTANYAAN USER: {question}
        """
        
        response = self.model.generate_content(prompt)
        return response.text