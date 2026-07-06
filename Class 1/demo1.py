import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv("../.env")

GROQ_API_KEY = os.getenv("GROQ_API")

client = Groq(api_key=GROQ_API_KEY)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Write a short story about a cat."}],
    temperature=0.7,
    max_tokens=100
)

print(completion.choices[0].message.content)