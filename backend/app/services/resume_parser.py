"""Resume processing: extract raw text, then use the LLM to structure it into
a profile (skills / technologies / domains / seniority).

Why LLM extraction over regex keyword matching:
  * Resumes are unstructured and phrasing varies wildly.
  * We want *normalised* skills ("Postgres" -> "PostgreSQL") and inferred
    seniority, which brittle keyword lists cannot provide.
A deterministic keyword fallback is kept for offline/robustness.
"""
from __future__ import annotations

import io

from app.services.llm import complete_json

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None


def extract_text_from_pdf_bytes(data: bytes) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is required to parse PDF resumes.")
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


_PROFILE_SYSTEM = (
    "You are an expert technical recruiter. Extract a structured profile from a "
    "resume. Return STRICT JSON only."
)


def build_profile(resume_text: str, role_label: str) -> dict:
    """Return {skills, technologies, domains, seniority, summary}."""
    text = resume_text[:8000]  # cap tokens; resumes rarely exceed this meaningfully
    prompt = f"""Analyse the following resume for a candidate applying to the role of "{role_label}".

Return JSON with exactly these keys:
- "skills": list of 5-12 concrete technical skills (concepts/methods).
- "technologies": list of 5-12 tools/languages/frameworks they have used.
- "domains": list of 1-5 domains/industries they have worked in.
- "seniority": one of "junior", "mid", "senior" inferred from experience.
- "summary": a 1-2 sentence professional summary.

Normalise names (e.g. "postgres" -> "PostgreSQL"). Only include items actually
supported by the resume text.

RESUME:
\"\"\"{text}\"\"\"
"""
    try:
        data = complete_json(prompt, system=_PROFILE_SYSTEM)
        if isinstance(data, dict):
            return _normalise_profile(data)
    except Exception:
        pass
    return _fallback_profile(resume_text)


def _normalise_profile(data: dict) -> dict:
    def _as_list(v):
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
        return []

    seniority = str(data.get("seniority", "mid")).lower()
    if seniority not in {"junior", "mid", "senior"}:
        seniority = "mid"
    return {
        "skills": _as_list(data.get("skills"))[:12],
        "technologies": _as_list(data.get("technologies"))[:12],
        "domains": _as_list(data.get("domains"))[:5],
        "seniority": seniority,
        "summary": str(data.get("summary", "")).strip(),
    }


_COMMON_TECH = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "SQL", "PostgreSQL",
    "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "FastAPI", "Flask",
    "Django", "React", "Node.js", "TensorFlow", "PyTorch", "scikit-learn", "Pandas",
    "NumPy", "Spark", "Kafka", "GraphQL", "Git",
]


def _fallback_profile(resume_text: str) -> dict:
    lower = resume_text.lower()
    techs = [t for t in _COMMON_TECH if t.lower() in lower]
    return {
        "skills": techs[:8],
        "technologies": techs[:12],
        "domains": [],
        "seniority": "mid",
        "summary": "Profile extracted via keyword fallback (LLM parsing unavailable).",
    }
