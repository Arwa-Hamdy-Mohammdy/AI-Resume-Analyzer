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

Compare the resume with the target job description.

IMPORTANT RULES:
- Respond with ONLY a valid JSON object.
- Do NOT write explanations or markdown code blocks (```json).
- "match_score" MUST be an integer between 0 and 100 representing overall ATS compatibility.
- "strengths" MUST ONLY contain candidate skills, tools, or experience that DIRECTLY MATCH the requirements of this target job. Do NOT list irrelevant candidate skills (e.g., do NOT list frontend skills like React for a backend Python role unless requested).
- "missing_skills" MUST contain required skills, frameworks, or experience from the job description that are missing in the candidate's resume.
- "recommendations" MUST contain 2 to 4 actionable recommendations for the candidate to improve their fit for this specific job.

Return exactly this JSON structure:
{{
    "match_score": 75,
    "missing_skills": ["Skill1", "Skill2"],
    "strengths": ["MatchedSkill1", "MatchedSkill2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
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
                    "role": "system",
                    "content": "You are a JSON ATS API. You return matching evaluation between a resume and a job description."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content