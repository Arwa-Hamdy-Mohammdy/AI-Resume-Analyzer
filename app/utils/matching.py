import json
import re

SYNONYM_MAP = {
    # Core Languages
    "py": ["python", "py", "python3", "python 3"],
    "python": ["python", "py", "python3", "python 3"],
    "js": ["javascript", "js", "ecmascript"],
    "javascript": ["javascript", "js", "ecmascript"],
    "ts": ["typescript", "ts"],
    "typescript": ["typescript", "ts"],
    "cpp": ["c++", "cpp"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net", "dotnet"],
    "csharp": ["c#", "csharp", ".net", "dotnet"],
    ".net": [".net", "dotnet", "c#", "csharp"],
    "dotnet": [".net", "dotnet", "c#", "csharp"],
    "java": ["java"],

    # Frontend Frameworks & Libraries
    "react": ["react", "reactjs", "react.js"],
    "reactjs": ["react", "reactjs", "react.js"],
    "react native": ["react native", "react-native"],
    "vue": ["vue", "vuejs", "vue.js", "nuxt"],
    "vuejs": ["vue", "vuejs", "vue.js"],
    "next": ["next", "nextjs", "next.js"],
    "nextjs": ["next", "nextjs", "next.js"],
    "angular": ["angular", "angularjs", "angular.js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap", "bootstrap5"],
    "redux": ["redux", "redux toolkit", "rtk"],

    # Backend & API Frameworks
    "node": ["node", "nodejs", "node.js"],
    "nodejs": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs", "express.js"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django", "django rest framework", "drf"],
    "api": ["api", "rest api", "restful api", "restful apis", "web apis", "rest", "restful"],
    "rest": ["api", "rest api", "restful api", "restful apis", "web apis", "rest", "restful"],
    "restful": ["api", "rest api", "restful api", "restful apis", "web apis", "rest", "restful"],
    "graphql": ["graphql", "apollo"],

    # Databases & Storage
    "sql": ["sql", "sqlite", "mysql", "postgresql", "psql", "rdbms"],
    "sqlite": ["sqlite", "sql"],
    "mysql": ["mysql", "sql"],
    "postgres": ["postgres", "postgresql", "psql", "sql"],
    "postgresql": ["postgres", "postgresql", "psql", "sql"],
    "mongo": ["mongo", "mongodb", "mongoose"],
    "mongodb": ["mongo", "mongodb", "mongoose"],
    "nosql": ["nosql", "mongodb", "redis", "dynamodb", "cassandra"],
    "redis": ["redis"],

    # DevOps, Cloud & Tools
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "azure": ["azure", "microsoft azure"],
    "k8s": ["k8s", "kubernetes"],
    "kubernetes": ["k8s", "kubernetes"],
    "docker": ["docker", "containerization", "containers", "docker-compose"],
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "github": ["git", "github", "version control"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "jenkins", "github actions"],

    # AI, Data Science & ML
    "ml": ["ml", "machine learning"],
    "machine learning": ["ml", "machine learning"],
    "ai": ["ai", "artificial intelligence", "genai", "generative ai"],
    "artificial intelligence": ["ai", "artificial intelligence"],
    "dl": ["dl", "deep learning"],
    "deep learning": ["dl", "deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "natural language processing": ["nlp", "natural language processing"],
    "cv": ["cv", "computer vision"],
    "computer vision": ["cv", "computer vision"],
    "rag": ["rag", "retrieval-augmented generation", "retrieval augmented generation"],
    "llm": ["llm", "llms", "large language models"],
    "llms": ["llm", "llms", "large language models"],

    # Roles & Domains
    "fe": ["frontend", "front-end", "front end", "fe"],
    "frontend": ["frontend", "front-end", "front end", "fe"],
    "be": ["backend", "back-end", "back end", "be"],
    "backend": ["backend", "back-end", "back end", "be"],
    "fullstack": ["fullstack", "full-stack", "full stack"],
    "full stack": ["fullstack", "full-stack", "full stack"]
}

FILLER_WORDS = [
    "experience with", "knowledge of", "proficiency in", "proficient in", "strong",
    "basic", "advanced", "good", "hands-on", "understanding of", "framework",
    "library", "development", "developer", "engineering", "engineer", "tools",
    "technology", "skills", "ability to"
]


def normalize_skill(skill: str) -> str:
    if not skill:
        return ""
    cleaned = str(skill).lower().strip()
    cleaned = re.sub(r'[^\w\s\.\+#-]', '', cleaned).strip()
    for filler in FILLER_WORDS:
        cleaned = re.sub(rf'\b{re.escape(filler)}\b', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def is_skill_matched(job_skill: str, resume_skills: list[str], resume_text: str = "") -> bool:
    if not job_skill:
        return False

    raw_job_skill = str(job_skill).lower().strip()
    norm_job_skill = normalize_skill(job_skill)
    
    if not norm_job_skill and not raw_job_skill:
        return False

    norm_resume_skills = [normalize_skill(rs) for rs in resume_skills if rs]
    raw_resume_skills = [str(rs).lower().strip() for rs in resume_skills if rs]

    # 1. Exact match or whole-phrase boundary match in extracted resume skills
    for rs, raw_rs in zip(norm_resume_skills, raw_resume_skills):
        if not rs and not raw_rs:
            continue
        if norm_job_skill and rs:
            if norm_job_skill == rs or re.search(rf'\b{re.escape(norm_job_skill)}\b', rs) or re.search(rf'\b{re.escape(rs)}\b', norm_job_skill):
                return True
        if raw_job_skill and raw_rs:
            if raw_job_skill == raw_rs or re.search(rf'\b{re.escape(raw_job_skill)}\b', raw_rs) or re.search(rf'\b{re.escape(raw_rs)}\b', raw_job_skill):
                return True

    # 2. Direct technical synonym matching
    job_synonyms = SYNONYM_MAP.get(norm_job_skill, SYNONYM_MAP.get(raw_job_skill, [norm_job_skill or raw_job_skill]))
    for rs in norm_resume_skills:
        rs_synonyms = SYNONYM_MAP.get(rs, [rs])
        for js_syn in job_synonyms:
            for rs_syn in rs_synonyms:
                if js_syn == rs_syn or (len(js_syn) > 2 and re.search(rf'\b{re.escape(js_syn)}\b', rs_syn)):
                    return True

    # 3. Search whole skill phrase or synonyms in raw resume_text using regex word boundaries
    if resume_text:
        lowered_text = resume_text.lower()
        search_terms = set([raw_job_skill, norm_job_skill] + job_synonyms)
        search_terms.discard("")
        for term in search_terms:
            if len(term) >= 2:
                pattern = rf'\b{re.escape(term)}\b'
                if re.search(pattern, lowered_text):
                    return True

    return False


def calculate_match_score(resume_skills: list[str], job_skills: list[str], resume_text: str = "") -> int:
    if not job_skills:
        return 0

    job_skills_cleaned = [s.strip() for s in job_skills if s and str(s).strip()]
    if not job_skills_cleaned:
        return 0

    matched_count = sum(1 for js in job_skills_cleaned if is_skill_matched(js, resume_skills, resume_text))
    return int((matched_count / len(job_skills_cleaned)) * 100)


def refine_match_results(resume_skills: list[str], job_skills: list[str], ai_missing: list[str], ai_strengths: list[str], resume_text: str = ""):
    """
    Cross-checks AI output against actual extracted resume skills AND raw resume text
    to guarantee zero false missing skills and strictly relevant matching strengths!
    """
    raw_strengths = ai_strengths if isinstance(ai_strengths, list) else []
    raw_missing = ai_missing if isinstance(ai_missing, list) else []

    clean_strengths = []
    clean_missing = []

    # 1. Process missing skills reported by AI:
    for missing_item in raw_missing:
        # Check if missing item is actually matched in resume skills or raw text
        if is_skill_matched(str(missing_item), resume_skills, resume_text):
            if missing_item not in clean_strengths:
                clean_strengths.append(missing_item)
        else:
            if missing_item not in clean_missing:
                clean_missing.append(missing_item)

    # 2. Ensure required job skills are correctly categorized
    for js in job_skills:
        if is_skill_matched(js, resume_skills, resume_text):
            if js not in clean_strengths:
                clean_strengths.append(js)
            if js in clean_missing:
                clean_missing.remove(js)
        else:
            if js not in clean_missing:
                clean_missing.append(js)

    # 3. Only keep AI strengths if candidate actually matches required job skills
    has_any_matched_job_skill = any(is_skill_matched(js, resume_skills, resume_text) for js in job_skills) if job_skills else True
    if not has_any_matched_job_skill:
        # If candidate has 0 matched job skills for this position, clear irrelevant candidate strengths
        clean_strengths = []
    else:
        for st in raw_strengths:
            st_str = str(st)
            if any(is_skill_matched(js, [st_str], st_str) for js in job_skills):
                if st_str not in clean_strengths:
                    clean_strengths.append(st_str)

    return clean_strengths, clean_missing


