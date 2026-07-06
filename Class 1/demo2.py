from dotenv import load_dotenv
import os
from google import genai

load_dotenv("../.env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API")

client = genai.Client(api_key=GOOGLE_API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain how AI works in a few words",
    config={
        "temperature": 0.7,
        "max_output_tokens": 500,
    },
)

print(response.text)
