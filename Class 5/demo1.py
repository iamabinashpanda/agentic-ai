import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

load_dotenv("../.env")

Settings.llm = Groq(model=os.getenv("GROQ_MODEL"), api_key=os.getenv("GROQ_API"))
Settings.embed_model = HuggingFaceEmbedding(model_name=os.getenv("HUGGINGFACEHUB_MODEL"))

lyft_file_path = Path("./lyft_2021.pdf")
documents = SimpleDirectoryReader(input_files=[lyft_file_path]).load_data()
index = VectorStoreIndex.from_documents(documents=documents)
query_engine = index.as_query_engine(similarity_top_k=5)

while True:
    user_input = input("Query: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if not user_input:
        continue

    try:
        response = query_engine.query(user_input)
        print(f"\nAnswer: {response}\n")
    except Exception as e:
        print(f"Error: {e}")

# how was lyft's profitability in 2021