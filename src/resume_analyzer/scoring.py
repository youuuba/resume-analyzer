"""Resume-to-job-description scoring.

Defines the ``MatchResult`` dataclass and ``score_match``. Pure: no I/O.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from resume_analyzer.parsing import Resume
from resume_analyzer.skills import extract_skills


@dataclass(frozen=True)
class MatchResult:
    """Skill overlap between a resume and a job description."""

    # Job description skills found in the resume, sorted.
    matched_skills: tuple[str, ...]
    # Job description skills not found in the resume, sorted.
    missing_skills: tuple[str, ...]
    # Percentage of job description skills that were matched, 0.0-100.0,
    # rounded half-up to one decimal. 0.0 when the job description
    # contains no known skills.
    coverage_score: float


def _coverage(matched: int, total: int) -> float:
    if total == 0:
        return 0.0
    # Decimal so that ties round up (1/16 -> 6.3); round() would give 6.2.
    percent = Decimal(matched * 100) / Decimal(total)
    return float(percent.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def score_match(resume: Resume, job_description: str) -> MatchResult:
    """Compare the skills in ``resume`` against those in ``job_description``.

    Skills are extracted from the resume's full text, not just its skills
    section, so skills mentioned under experience or projects count.
    """
    required = extract_skills(job_description)
    present = extract_skills(resume.raw_text)
    matched = required & present
    return MatchResult(
        matched_skills=tuple(sorted(matched)),
        missing_skills=tuple(sorted(required - present)),
        coverage_score=_coverage(len(matched), len(required)),
    )
