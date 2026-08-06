import json


def calculate_match_score(resume_skills, job_skills):
    """
    Calculates the percentage of matching skills using partial & substring matching.
    """
    if not job_skills:
        return 0

    resume_skills_lower = [s.lower().strip() for s in resume_skills if s]
    job_skills_cleaned = [s.lower().strip() for s in job_skills if s.strip()]

    if not job_skills_cleaned:
        return 0

    matched_count = 0

    for job_skill in job_skills_cleaned:
        is_match = False
        for rs in resume_skills_lower:
            if job_skill in rs or rs in job_skill:
                is_match = True
                break
            # Match keywords longer than 3 chars
            js_words = [w for w in job_skill.split() if len(w) > 3]
            if any(w in rs for w in js_words):
                is_match = True
                break

        if is_match:
            matched_count += 1

    return int((matched_count / len(job_skills_cleaned)) * 100)