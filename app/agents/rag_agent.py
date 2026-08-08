import json
from huggingface_hub import InferenceClient
from app.core.config import HF_TOKEN

client = InferenceClient(api_key=HF_TOKEN)


class RAGAgent:

    def optimize_bullets(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        missing_skills: list[str],
        rag_context: str
    ) -> str:
        
        skills_str = ", ".join(missing_skills) if missing_skills else "General ATS alignment"
        
        prompt = f"""
You are an Expert ATS Resume Specialist & Career Coach.

Your job is to rewrite and optimize candidate resume bullet points specifically tailored for the target job position.

RETRIEVED ATS RULES & BEST PRACTICES (KNOWLEDGE BASE):
{rag_context}

TARGET JOB POSITION: {job_title}
JOB DESCRIPTION:
{job_description}

MISSING SKILLS TO WEAVE IN: {skills_str}

CANDIDATE CURRENT RESUME TEXT:
{resume_text}

INSTRUCTIONS:
1. Return ONLY a valid JSON object matching the JSON schema below.
2. Produce 4 to 6 strong, action-oriented, metrics-driven bullet points formatted with the STAR method (Action Verb + Context + Result/Metric).
3. Naturally weave in the missing skills and relevant target job keywords.
4. Do NOT use markdown outside the JSON. Do NOT write explanations.

SCHEMA:
{{
    "job_title": "{job_title}",
    "optimized_bullets": [
        "Architected and deployed scalable RESTful APIs using FastAPI and PostgreSQL, reducing latency by 35% across 10,000+ daily requests.",
        "Engineered responsive frontend UI components using React.js and TypeScript, increasing user engagement metrics by 25%."
    ],
    "ats_tips": [
        "Tip on how to highlight these bullets in your CV"
    ]
}}
"""

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a JSON API returning tailored ATS resume bullets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        return response.choices[0].message.content.strip()

    def generate_roadmap(
        self,
        missing_skills: list[str],
        rag_context: str
    ) -> str:

        skills_str = ", ".join(missing_skills) if missing_skills else "Software Engineering Skills"

        prompt = f"""
You are a Senior Technical Mentor & Career Adviser.

Your job is to generate a practical step-by-step learning roadmap and free course recommendations for missing technical skills.

RETRIEVED KNOWLEDGE BASE ROADMAPS & COURSES:
{rag_context}

TARGET MISSING SKILLS: {skills_str}

INSTRUCTIONS:
1. Return ONLY a valid JSON object.
2. Provide a structured step-by-step learning path for each missing skill.
3. Recommend free resources, key concepts, and practical project ideas.

SCHEMA:
{{
    "skills_analyzed": ["Skill1", "Skill2"],
    "roadmap": [
        {{
            "skill": "Skill Name",
            "estimated_time": "1-2 weeks",
            "key_concepts": ["Concept 1", "Concept 2"],
            "recommended_resources": ["Resource 1", "Resource 2"],
            "practice_project": "Build a mini project"
        }}
    ]
}}
"""

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a JSON API returning technical skill roadmaps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        return response.choices[0].message.content.strip()
