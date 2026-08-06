import json

from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN


client = InferenceClient(
    api_key=HF_TOKEN
)


class JobMatchAgent:

    def match(
        self,
        resume_text: str,
        job_description: str
    ):

        prompt = f"""
You are an ATS and HR expert.

Compare the resume with the job description.

IMPORTANT RULES:

- Respond with ONLY a JSON object.
- Do NOT write explanations.
- Do NOT write "Here is the JSON".
- Do NOT use markdown.
- Do NOT use ```json.
- Do NOT add reasoning.
- "match_score" MUST be a calculated integer between 0 and 100 based on how well the resume matches the job description.
- Output must start with {{
- Output must end with }}

Return exactly this JSON schema structure (calculate the actual match_score number, do not keep 0):

{{
    "match_score": 75,
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
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content