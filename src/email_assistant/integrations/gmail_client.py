"""Gmail read-only adapter. OAuth credentials must be created server-side."""

from __future__ import annotations

import base64
import re
from email.utils import parseaddr
from html.parser import HTMLParser
from typing import Any

from email_assistant.models.email import EmailMessage

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
ALLOWED_HEADERS = {"from", "subject", "date", "list-unsubscribe"}


class GmailIntegrationError(RuntimeError):
    """Provider errors without sensitive payloads."""


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "head"}:
            self.hidden += 1
        elif tag in {"p", "div", "br", "li", "tr"} and not self.hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "head"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "div", "br", "li", "tr"} and not self.hidden:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def _body(payload: dict[str, Any], max_chars: int) -> str:
    plain: list[str] = []
    html: list[str] = []

    def visit(part: dict[str, Any]) -> None:
        mime = str(part.get("mimeType", "")).lower()
        data = (part.get("body") or {}).get("data", "")
        if data and mime in {"text/plain", "text/html"}:
            try:
                decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode(
                    "utf-8", errors="replace"
                )
            except (ValueError, TypeError):
                decoded = ""
            (plain if mime == "text/plain" else html).append(decoded)
        for child in part.get("parts", []) or []:
            if isinstance(child, dict):
                visit(child)

    visit(payload)
    result = " ".join(plain)
    if not result and html:
        parser = _HTMLText()
        parser.feed(" ".join(html))
        result = " ".join(parser.parts)
    return re.sub(r"\s+", " ", result).strip()[:max_chars]


def normalize_gmail_message(raw: dict[str, Any], max_chars: int = 20_000) -> EmailMessage:
    payload = raw.get("payload") or {}
    headers: dict[str, str] = {}
    for item in payload.get("headers", []) or []:
        key = str(item.get("name", "")).lower()
        if key in ALLOWED_HEADERS:
            headers[key] = str(item.get("value", ""))[:2000]
    return EmailMessage(
        provider_id=str(raw.get("id", ""))[:256],
        thread_id=str(raw.get("threadId", ""))[:256],
        sender=parseaddr(headers.get("from", ""))[1][:320],
        subject=headers.get("subject", "")[:998],
        body_text=_body(payload, max_chars),
        received_at=headers.get("date", "")[:128],
        headers={"List-Unsubscribe": headers["list-unsubscribe"]}
        if "list-unsubscribe" in headers
        else {},
    )


class GmailReadOnlyClient:
    """Only exposes read/list methods and refuses credentials with broader scopes."""

    def __init__(self, credentials: Any, max_email_chars: int = 20_000) -> None:
        if not hasattr(credentials, "has_scopes") or not credentials.has_scopes(
            [GMAIL_READONLY_SCOPE]
        ):
            raise GmailIntegrationError("Gmail read-only OAuth scope is required")
        if not 1000 <= max_email_chars <= 100000:
            raise ValueError("max_email_chars must be between 1000 and 100000")
        try:
            from googleapiclient.discovery import build

            self._service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        except Exception as exc:
            raise GmailIntegrationError("Gmail client initialization failed") from exc
        self._max_email_chars = max_email_chars

    def list_recent(self, max_results: int = 10) -> list[EmailMessage]:
        count = max(1, min(int(max_results), 20))
        try:
            response = self._service.users().messages().list(
                userId="me", maxResults=count, q="newer_than:30d"
            ).execute()
            output = []
            for item in (response.get("messages", []) or [])[:count]:
                message_id = str(item.get("id", ""))
                if not message_id or len(message_id) > 256:
                    continue
                raw = self._service.users().messages().get(
                    userId="me", id=message_id, format="full"
                ).execute()
                output.append(normalize_gmail_message(raw, self._max_email_chars))
            return output
        except Exception as exc:
            raise GmailIntegrationError("Gmail read request failed") from exc
