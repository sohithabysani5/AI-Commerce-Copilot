import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Hello! Explain what an AI Commerce Copilot is in one simple sentence."
)

print("\nGemini Response:")
print(response.text)