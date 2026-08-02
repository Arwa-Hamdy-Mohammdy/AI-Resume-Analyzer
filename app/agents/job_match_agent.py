import json

from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN


client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


class JobMatchAgent:

    def match(
        self,
        resume_text: str,
        job_description: str
    ):

        prompt = f"""
You are an AI Resume Matcher.

Compare the resume with the job description.

Return ONLY valid JSON.

{{
    "match_score": 0,
    "missing_skills": [],
    "strengths": [],
    "recommendations": []
}}

Resume:

{resume_text}

Job Description:

{job_description}
"""

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content