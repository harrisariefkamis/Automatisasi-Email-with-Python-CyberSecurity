"""Use-case layer connected to the existing deterministic triage function."""

from dataclasses import dataclass
from typing import Any

from email_assistant.core import as_jsonable, triage_email
from email_assistant.models.email import EmailMessage


@dataclass(frozen=True)
class EmailTriage:
    email: EmailMessage
    rules_result: dict[str, Any]
    ai_result: dict[str, Any] | None = None


def triage_message(
    email: EmailMessage,
    ai_client: Any | None = None,
    *,
    external_processing_consent: bool = False,
) -> EmailTriage:
    rules_result = as_jsonable(triage_email(email.as_triage_input()))
    ai_result = None
    if ai_client is not None and rules_result.get("category") == "job":
        if external_processing_consent is not True:
            raise PermissionError("Explicit consent is required before AI processing")
        try:
            result = ai_client.analyze_job_email(
                email.subject,
                email.body_text,
                external_processing_consent=True,
            )
            ai_result = result.model_dump()
        except Exception:
            # Keep deterministic result; do not log provider errors or email contents.
            ai_result = None
    return EmailTriage(email=email, rules_result=rules_result, ai_result=ai_result)
