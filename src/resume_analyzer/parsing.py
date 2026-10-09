"""Resume parsing.

Defines the ``Resume`` dataclass and ``parse_resume``, which splits plain
text into sections by common heading patterns. Pure: no I/O.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Resume:
    """A resume split into sections. Each section is its raw text block."""

    contact: str
    experience: str
    education: str
    skills: str
    # The full original text, including sections not captured above
    # (summary, projects, certifications, ...).
    raw_text: str


_OTHER = "other"

# Normalized heading text -> section it starts. Headings mapped to _OTHER
# are recognized only so that they end the previous section.
_HEADINGS: dict[str, str] = {
    **dict.fromkeys(
        ("contact", "contact information", "contact info", "contact details",
         "personal information", "personal details"),
        "contact",
    ),
    **dict.fromkeys(
        ("experience", "work experience", "professional experience",
         "relevant experience", "employment", "employment history",
         "work history", "career history"),
        "experience",
    ),
    **dict.fromkeys(
        ("education", "education and training", "academic background",
         "academic history"),
        "education",
    ),
    **dict.fromkeys(
        ("skills", "technical skills", "core skills", "key skills",
         "skills and tools", "tools and technologies", "technologies",
         "tech stack", "core competencies", "competencies"),
        "skills",
    ),
    **dict.fromkeys(
        ("summary", "professional summary", "profile", "professional profile",
         "objective", "career objective", "about", "about me", "projects",
         "personal projects", "certifications", "certificates", "awards",
         "honors", "achievements", "publications", "languages", "interests",
         "volunteering", "volunteer experience", "references"),
        _OTHER,
    ),
}

# Markdown and plain-text decoration around headings: "## Skills", "**Skills**",
# "SKILLS:", "=== Skills ===".
_DECORATION = "#*=_-~: \t"


def _normalize_heading(text: str) -> str:
    text = text.strip(_DECORATION).lower().replace("&", " and ")
    return " ".join(text.split())


def _match_heading(line: str) -> tuple[str, str] | None:
    """Return (section, inline content) if ``line`` is a heading, else None."""
    section = _HEADINGS.get(_normalize_heading(line))
    if section is not None:
        return section, ""
    # Inline form: "Skills: Python, Docker".
    head, sep, rest = line.partition(":")
    rest = rest.strip(" \t*_")
    if sep and rest:
        section = _HEADINGS.get(_normalize_heading(head))
        if section is not None:
            return section, rest
    return None


def parse_resume(text: str) -> Resume:
    """Split plain-text resume ``text`` into sections by heading.

    Lines before the first recognized heading are treated as contact
    information. Content under unrecognized-but-known headings (summary,
    projects, ...) is kept only in ``raw_text``. A resume with no
    recognizable headings ends up entirely in ``contact``.
    """
    sections: dict[str, list[str]] = {
        "contact": [], "experience": [], "education": [], "skills": [], _OTHER: [],
    }
    current = "contact"
    for line in text.splitlines():
        heading = _match_heading(line)
        if heading is None:
            sections[current].append(line)
            continue
        current, inline = heading
        if inline:
            sections[current].append(inline)

    def block(name: str) -> str:
        return "\n".join(sections[name]).strip()

    return Resume(
        contact=block("contact"),
        experience=block("experience"),
        education=block("education"),
        skills=block("skills"),
        raw_text=text,
    )
