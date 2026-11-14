"""Authenticated Vercel serverless handler for manual-text triage only."""

from __future__ import annotations

import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

# The repository uses a src/ layout. Vercel may run functions without installing
# the local project package, so add the source directory explicitly and safely.
_SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(_SOURCE_DIR))

from email_assistant.core import as_jsonable, triage_email  # noqa: E402

MAX_BODY_BYTES = 32_000
MAX_FIELD_CHARS = 20_000


class handler(BaseHTTPRequestHandler):
    """Vercel-compatible Python handler; no Gmail, Supabase, or AI calls."""

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self._send(405, {"error": "method_not_allowed", "allowed": ["POST"]})

    def do_POST(self) -> None:  # noqa: N802
        expected = os.environ.get("API_ACCESS_TOKEN", "")
        supplied = self.headers.get("Authorization", "")
        if not expected or not hmac.compare_digest(supplied, f"Bearer {expected}"):
            self._send(401, {"error": "unauthorized"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send(415, {"error": "application/json required"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except (ValueError, TypeError):
            self._send(400, {"error": "invalid content length"})
            return
        if not 1 <= length <= MAX_BODY_BYTES:
            self._send(413, {"error": "invalid request size"})
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("incomplete request")
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("JSON object required")
            allowed = ("from", "subject", "body")
            email = {key: value.get(key, "") for key in allowed}
            if any(not isinstance(item, str) or len(item) > MAX_FIELD_CHARS for item in email.values()):
                raise ValueError("invalid field")
            result = as_jsonable(triage_email(email))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            self._send(400, {"error": "invalid request"})
            return
        except Exception:
            # Never serialize or log user content or internal exception details.
            self._send(500, {"error": "internal error"})
            return
        self._send(200, {"triage": result})

    def log_message(self, fmt: str, *args: object) -> None:
        # Avoid default request logging that may contain user data.
        return
