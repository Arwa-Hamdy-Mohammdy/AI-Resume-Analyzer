from huggingface_hub import InferenceClient
from app.core.config import HF_TOKEN

client = InferenceClient(api_key=HF_TOKEN)


class ResumeAgent:

    def analyze_resume(self, resume_text: str):

        prompt = f"""
You are a Resume Parsing API.

Your job is ONLY to extract information from the resume.

IMPORTANT RULES:

- Return ONLY a valid JSON object.
- Do NOT explain anything.
- Do NOT add any text before the JSON.
- Do NOT add any text after the JSON.
- Do NOT use markdown.
- Do NOT use ```json.
- Every key must exist.
- If information is missing, return an empty string or empty list.

Return EXACTLY this schema:

{{
    "summary": "",
    "skills": [],
    "education": [],
    "experience": []
}}

Resume:

{resume_text}
"""

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON API. You ONLY return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=700
        )

        return response.choices[0].message.content.strip()