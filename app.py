"""Vercel root Python entrypoint.

The Streamlit demo lives in ``streamlit_app.py`` and is run with Streamlit locally.
Vercel's Python runtime needs a top-level ``handler`` export, so the root entrypoint
re-exports the stateless triage API handler.
"""

from api.triage import handler

__all__ = ["handler"]
