"""Authenticated, stateless Vercel endpoint for manual-text triage only."""

from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler

from email_assistant.core import as_jsonable, triage_email

MAX_BODY_BYTES = 32_000


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        expected = os.environ.get("API_ACCESS_TOKEN", "")
        if not expected or not hmac.compare_digest(
            self.headers.get("Authorization", ""), f"Bearer {expected}"
        ):
            self._send(401, {"error": "unauthorized"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send(415, {"error": "application/json required"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, {"error": "invalid content length"})
            return
        if not 1 <= size <= MAX_BODY_BYTES:
            self._send(413, {"error": "invalid request size"})
            return
        try:
            value = json.loads(self.rfile.read(size))
            if not isinstance(value, dict):
                raise ValueError
            email = {key: value.get(key, "") for key in ("from", "subject", "body")}
            if any(not isinstance(item, str) for item in email.values()):
                raise ValueError
            result = as_jsonable(triage_email(email))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            self._send(400, {"error": "invalid request"})
            return
        self._send(200, {"triage": result})

    def log_message(self, fmt: str, *args: object) -> None:
        return
