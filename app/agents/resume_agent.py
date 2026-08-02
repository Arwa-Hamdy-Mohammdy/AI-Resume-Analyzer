from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN


client = InferenceClient(
    api_key=HF_TOKEN
)


class ResumeAgent:

    def analyze_resume(self, resume_text: str):

        prompt = f"""
You are an expert AI Resume Analyzer.

Analyze the following resume.

Return ONLY valid JSON.

Do not write explanations.
Do not use markdown.
Do not wrap the JSON inside ```json.
Do not add any text before or after the JSON.

Use this exact structure:

{{
    "name": "",
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
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=1000
        )

        return response.choices[0].message.content