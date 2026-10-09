"""Resume analyzer: compare a resume against a job description by skill overlap.

The core modules (parsing, skills, scoring) are pure and have no web
dependencies. The FastAPI app lives in ``resume_analyzer.api`` and is never
imported from here, so the core stays importable without starting a server.
"""
