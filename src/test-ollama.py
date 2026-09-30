import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()

ollama_url = os.getenv("OLLAMA_URL")
ollama_model = os.getenv("OLLAMA_MODEL")

client = Client(host=ollama_url)

response = client.chat(
    model=ollama_model,
    messages=[
        {
            "role": "user",
            "content": "What is a supplier? Answer in one sentence."
        }
    ]
)

print(response.message.content)
