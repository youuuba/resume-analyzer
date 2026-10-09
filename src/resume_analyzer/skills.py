"""Curated skill vocabulary and skill extraction.

Holds the canonical skill names with their aliases, and ``extract_skills``,
which finds them in free text. Pure: no I/O.
"""

import re

# Canonical skill name -> extra terms that count as evidence of it: other
# spellings, or more specific skills that imply it ("mysql" implies "sql").
# The canonical name is always matched too. Everything is lowercase.
#
# Terms that collide with ordinary English or single letters are left out
# on purpose: "go" (use "golang"), "r", "c", bare "node", bare "rest".
SKILLS: dict[str, tuple[str, ...]] = {
    # Languages
    "python": ("python3",),
    "java": (),
    "javascript": ("js", "ecmascript"),
    "typescript": (),
    "c++": ("cpp",),
    "c#": ("csharp", "c sharp"),
    "golang": (),
    "rust": (),
    "sql": ("mysql", "postgresql", "postgres"),
    # Web and backend
    "fastapi": (),
    "django": (),
    "flask": (),
    "react": ("reactjs", "react.js"),
    "node.js": ("nodejs",),
    "rest api": ("rest apis", "restful", "restful api", "restful apis"),
    "graphql": (),
    # Data, ML and AI
    "machine learning": ("ml",),
    "deep learning": (),
    "nlp": ("natural language processing",),
    "computer vision": (),
    "pytorch": (),
    "tensorflow": (),
    "scikit-learn": ("sklearn", "scikit learn"),
    "pandas": (),
    "numpy": (),
    "llm": ("llms", "large language model", "large language models"),
    "rag": ("retrieval-augmented generation", "retrieval augmented generation"),
    "prompt engineering": (),
    "hugging face": ("huggingface",),
    "langchain": (),
    "mlops": (),
    "spark": ("apache spark", "pyspark"),
    "airflow": ("apache airflow",),
    # Infrastructure and tooling
    "docker": (),
    "kubernetes": ("k8s",),
    "aws": ("amazon web services",),
    "gcp": ("google cloud", "google cloud platform"),
    "azure": (),
    "terraform": (),
    "ci/cd": ("cicd", "ci cd", "continuous integration"),
    "git": ("github", "gitlab"),
    "linux": (),
    # Datastores
    "mysql": (),
    "postgresql": ("postgres",),
    "mongodb": ("mongo",),
    "redis": (),
}


def _compile(term: str) -> str:
    # Words may be separated by any run of whitespace.
    body = r"\s+".join(re.escape(word) for word in term.split())
    # Custom boundaries instead of \b, which breaks on "c++", "c#", "node.js".
    # A preceding "." also blocks a match, so the "js" in "node.js" is not
    # read as javascript.
    return rf"(?<![a-z0-9.]){body}(?![a-z0-9])"


_PATTERNS: dict[str, re.Pattern[str]] = {
    skill: re.compile("|".join(_compile(t) for t in (skill, *aliases)))
    for skill, aliases in SKILLS.items()
}


def extract_skills(text: str) -> set[str]:
    """Return the canonical names of every known skill mentioned in ``text``."""
    lowered = text.lower()
    return {skill for skill, pattern in _PATTERNS.items() if pattern.search(lowered)}
