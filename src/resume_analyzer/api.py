"""FastAPI application.

Thin HTTP layer: request validation, a call into the core modules, and the
response. No business logic lives here.
"""

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, StringConstraints

from resume_analyzer.parsing import parse_resume
from resume_analyzer.scoring import MatchResult, score_match

# Non-empty after trimming whitespace, capped to bound request size.
InputText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100_000)
]


class AnalyzeRequest(BaseModel):
    resume_text: InputText
    job_description: InputText


app = FastAPI(
    title="Resume Analyzer",
    description="Compare a resume against a job description by skill overlap.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> MatchResult:
    return score_match(parse_resume(request.resume_text), request.job_description)
