from huggingface_hub import InferenceClient
from app.core.config import HF_TOKEN

client = InferenceClient(api_key=HF_TOKEN)


class ResumeAgent:

    def analyze_resume(self, resume_text: str):

        prompt = f"""
You are an expert Resume Analyzer & Parsing API.

Your job is to analyze the resume and extract structured information.

IMPORTANT RULES:
- Return ONLY a valid JSON object.
- Do NOT explain anything.
- Do NOT add any text before or after the JSON.
- Do NOT use markdown code blocks (```json).
- Every key must exist.
- Separate technical hard skills (programming languages, frameworks, tools) from soft interpersonal skills.
- CRITICAL: Every item in "technical_skills" and "soft_skills" MUST be a short, clean skill name (1 to 3 words max, e.g., ["Python", "FastAPI", "React", "Docker", "PostgreSQL", "JavaScript"]).
- NEVER include full sentences, paragraphs, bullet points, or descriptions inside "technical_skills" or "soft_skills".
- Evaluate candidate strengths and areas for improvement (weaknesses).
- Calculate an overall_score (integer between 0 and 100) representing resume quality and completeness.

Return EXACTLY this JSON schema structure:

{{
    "summary": "Executive summary of the candidate",
    "skills": ["Combined list of short skill names"],
    "technical_skills": ["Short technical skill names"],
    "soft_skills": ["Short soft skill names"],
    "education": ["Education degrees, universities, years"],
    "experience": ["Work history roles, companies, dates"],
    "strengths": ["Key candidate strengths"],
    "weaknesses": ["Key areas for improvement"],
    "overall_score": 85
}}

Resume:

{resume_text}
"""

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON API. You ONLY return valid JSON with short 1-3 word skill tags."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=900
        )

        return response.choices[0].message.content.strip()
