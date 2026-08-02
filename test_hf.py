from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
    max_tokens=100,
    temperature=0
)

print(response)
print("--------------------------------")
print(response.choices[0].message.content)