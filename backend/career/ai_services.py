import re
from pathlib import Path

SKILL_DICTIONARY = [
    "Python", "Django", "Django REST Framework", "JavaScript", "React", "HTML", "CSS",
    "PostgreSQL", "MySQL", "SQL", "REST API", "Git", "GitHub", "Docker", "AWS",
    "Machine Learning", "NLP", " scikit-learn", "Java", "C", "C++", "Node.js",
    "TypeScript", "Bootstrap", "Tailwind CSS", "Pytest", "Linux", "Redis"
]
NORMALIZED = {s.strip().lower(): s.strip() for s in SKILL_DICTIONARY}

def extract_resume_text(file_path):
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        import fitz
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    if suffix == ".docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Only PDF and DOCX files are supported.")

def extract_skills(text):
    haystack = re.sub(r"\s+", " ", text.lower())
    found = []
    for key, display in NORMALIZED.items():
        if key and re.search(r"(?<![a-z0-9])" + re.escape(key) + r"(?![a-z0-9])", haystack):
            found.append(display)
    return sorted(set(found))

def calculate_match(candidate_skills, job_skills, candidate_experience=0, required_experience=0):
    candidate = {s.strip().lower() for s in candidate_skills if s.strip()}
    required = {s.strip().lower() for s in job_skills if s.strip()}
    if not required:
        return {"score": 0, "matched_skills": [], "missing_skills": [], "explanation": "The recruiter has not specified required skills."}
    matched = sorted(candidate & required)
    missing = sorted(required - candidate)
    skill_score = len(matched) / len(required) * 100
    if required_experience <= 0:
        experience_score = 100
    else:
        experience_score = min(candidate_experience / required_experience, 1) * 100
    score = round(skill_score * 0.85 + experience_score * 0.15)
    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "explanation": f"{len(matched)} of {len(required)} listed skills matched. Experience contributes 15% of this advisory score."
    }

QUESTION_BANK = {
    "frontend developer": {
        "Beginner": [
            ("What is semantic HTML and why is it useful?", ["semantic", "meaning", "accessibility", "structure"]),
            ("Explain the CSS box model.", ["content", "padding", "border", "margin"]),
        ],
        "Intermediate": [
            ("What is the difference between state and props in React?", ["state", "props", "component", "parent"]),
            ("Explain the JavaScript event loop.", ["call stack", "event loop", "queue", "asynchronous"]),
        ],
        "Advanced": [
            ("How would you improve performance in a large React application?", ["memo", "lazy", "code splitting", "profiling", "render"]),
            ("Explain how browser rendering works and how you would reduce layout shifts.", ["DOM", "CSSOM", "layout", "paint", "reflow"]),
        ],
    },
    "python developer": {
        "Beginner": [
            ("What is the difference between a list and a tuple?", ["mutable", "immutable", "list", "tuple"]),
            ("What are Python dictionaries?", ["key", "value", "hash", "mapping"]),
        ],
        "Intermediate": [
            ("Explain decorators in Python with a practical use case.", ["function", "wrapper", "decorator", "metadata"]),
            ("How does Django ORM work?", ["model", "queryset", "database", "query"]),
        ],
        "Advanced": [
            ("How would you design a scalable Django REST API?", ["pagination", "serializer", "permissions", "index", "cache"]),
            ("Explain Python concurrency options and when you would use each.", ["thread", "process", "asyncio", "GIL"]),
        ],
    },
    "backend developer": {
        "Beginner": [
            ("What is a REST API?", ["resource", "http", "method", "stateless"]),
            ("What is a primary key in a database?", ["unique", "identify", "row", "constraint"]),
        ],
        "Intermediate": [
            ("How do database indexes improve query performance?", ["index", "lookup", "write", "query"]),
            ("Explain authentication versus authorization.", ["identity", "permission", "authentication", "authorization"]),
        ],
        "Advanced": [
            ("How would you prevent duplicate payment or order requests in an API?", ["idempotency", "transaction", "unique", "lock"]),
            ("Describe a strategy for scaling a Django application.", ["cache", "database", "worker", "load", "monitor"]),
        ],
    },
    "full stack developer": {
        "Beginner": [
            ("What happens when a React app calls a Django API?", ["request", "http", "response", "json"]),
            ("What is the purpose of a relational database?", ["table", "relationship", "constraint", "query"]),
        ],
        "Intermediate": [
            ("How do you manage authentication between React and Django?", ["token", "jwt", "authorization", "refresh"]),
            ("How would you design a job application data model?", ["user", "job", "foreign key", "constraint"]),
        ],
        "Advanced": [
            ("How would you design a reliable resume processing workflow?", ["validation", "background", "retry", "storage", "status"]),
            ("How would you secure a full-stack application?", ["permission", "validation", "https", "secret", "csrf"]),
        ],
    },
    "ai/ml developer": {
        "Beginner": [
            ("What is the difference between supervised and unsupervised learning?", ["label", "unlabel", "supervised", "unsupervised"]),
            ("What is overfitting?", ["training", "generalize", "validation", "complexity"]),
        ],
        "Intermediate": [
            ("Explain precision and recall.", ["true positive", "false positive", "false negative", "precision", "recall"]),
            ("How can text be converted into numerical features?", ["token", "vector", "tf-idf", "embedding"]),
        ],
        "Advanced": [
            ("How would you evaluate a semantic job matching model?", ["precision", "recall", "ranking", "dataset", "bias"]),
            ("How would you monitor drift in a deployed ML system?", ["distribution", "drift", "monitor", "retrain", "metric"]),
        ],
    },
}

def evaluate_answer(role, question, answer):
    words = [w for w in re.findall(r"[a-zA-Z0-9+#.]+", answer.lower()) if len(w) > 2]
    if len(words) < 8:
        return 20, {"summary": "Your answer is too brief to assess reliably. Add a definition, explanation and example.", "strengths": [], "missing_concepts": ["A clear explanation", "A practical example"], "next_step": "Write 3–6 sentences and include a relevant example."}
    q_lower = question.lower()
    bank = []
    for role_key, levels in QUESTION_BANK.items():
        if role_key in role.lower():
            for items in levels.values():
                for q, keywords in items:
                    if q == question:
                        bank = keywords
    if not bank:
        bank = [w for w in re.findall(r"[a-zA-Z]{5,}", q_lower)[:8]]
    present = [k for k in bank if k in answer.lower()]
    score = min(95, max(30, round((len(present) / max(len(bank), 1)) * 80 + min(len(words), 100) / 100 * 15)))
    missing = [k for k in bank if k not in answer.lower()]
    return score, {
        "summary": "This is an automated keyword-and-structure practice rubric, not a human assessment.",
        "strengths": present[:5],
        "missing_concepts": missing[:6],
        "next_step": "Improve the answer by defining the concept, explaining how it works, and giving a practical example."
    }
