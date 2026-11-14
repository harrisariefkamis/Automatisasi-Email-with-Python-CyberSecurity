"""Normalized, provider-independent email representation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    provider_id: str
    thread_id: str
    sender: str
    subject: str
    body_text: str
    received_at: str
    headers: dict[str, str]

    def as_triage_input(self) -> dict[str, object]:
        return {
            "from": self.sender,
            "subject": self.subject,
            "body": self.body_text,
            "headers": dict(self.headers),
        }
