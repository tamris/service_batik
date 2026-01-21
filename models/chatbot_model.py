import os
from google import genai
from google.genai import types # Untuk konfigurasi generasi

class ChatbotModel:
    def __init__(self, vector_db=None):
        # Inisialisasi Client baru
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Konfigurasi generasi versi SDK baru
        self.config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=512,
        )
        self.vector_db = vector_db

    def ask_ai(self, question):
        context = ""
        if self.vector_db:
            retriever = self.vector_db.as_retriever(search_kwargs={"k":7})
            docs = retriever.invoke(question)
            context = "\n".join([d.page_content for d in docs])

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
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=self.config
        )
        return response.text