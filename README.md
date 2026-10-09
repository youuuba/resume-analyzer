# Resume Analyzer

Compares a plain-text resume against a plain-text job description and reports
which skills overlap, which are missing, and a coverage score.

## Run it

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
uvicorn resume_analyzer.api:app --reload
```

The API is then at http://127.0.0.1:8000, with interactive docs at `/docs`.

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Skills: Python, MySQL, Docker", "job_description": "Python, SQL and Kubernetes"}'
```

```json
{"matched_skills": ["python", "sql"], "missing_skills": ["kubernetes"], "coverage_score": 66.7}
```

| Endpoint | Body | Returns |
|---|---|---|
| `POST /analyze` | `{"resume_text": str, "job_description": str}` | matched skills, missing skills, coverage score |
| `GET /health` | none | `{"status": "ok"}` |

Both text fields must be non-empty after trimming whitespace and at most
100,000 characters. Anything else gets a 422.

The core logic has no web dependencies and can be used directly:

```python
from resume_analyzer.parsing import parse_resume
from resume_analyzer.scoring import score_match

result = score_match(parse_resume(resume_text), job_description)
```

## How scoring works

- Skills come from a curated list of 46 terms in
  [`skills.py`](src/resume_analyzer/skills.py). Each skill has aliases
  (`k8s` counts as `kubernetes`), and some skills imply others (`mysql` and
  `postgresql` also count as `sql`). Matching is case-insensitive.
- The resume's whole text is searched, not just its Skills section, so skills
  mentioned under Experience or Projects count.
- `coverage_score` = matched / skills found in the job description × 100,
  rounded half-up to one decimal.
- **If the job description contains none of the known skills, the score is
  `0.0` and both lists are empty.** Read that as "nothing to compare", not as
  a poor match.

## What this deliberately does not do

- **No semantic understanding.** No LLMs, embeddings or NLP libraries. A skill
  counts only if it appears in the curated list, spelled one of the listed ways.
- **No ambiguous terms.** Go, R and C aren't detected, because matching them
  produces false positives on ordinary English. Write "Golang" to be detected.
- **No weighting.** Every skill in the job description counts as required,
  including "nice to have" ones, and years of experience are ignored.
- **Plain text only.** No PDF or DOCX parsing.
- **No storage, auth or deployment setup.** No database, no user accounts,
  no Docker.
