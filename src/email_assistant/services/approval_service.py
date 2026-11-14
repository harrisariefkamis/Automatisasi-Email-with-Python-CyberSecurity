"""Approval records only; deliberately no Gmail mutation/execution path exists."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets

from email_assistant.storage.audit import AuditSink, make_audit_event

ALLOWED_ACTIONS = {"apply_label", "move_to_trash", "unsubscribe"}


@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    actor_id: str
    resource_id: str
    action: str
    preview: str
    expires_at: datetime


class ApprovalService:
    """Create and record consent for review; this service cannot execute actions."""

    def __init__(self, audit_sink: AuditSink) -> None:
        self._audit = audit_sink

    def propose(self, actor_id: str, resource_id: str, action: str, preview: str) -> ActionProposal:
        if action not in ALLOWED_ACTIONS:
            raise ValueError("Action is not allowlisted")
        if not actor_id or not resource_id or not preview or len(preview) > 500:
            raise ValueError("Actor, resource, and a short preview are required")
        proposal = ActionProposal(
            secrets.token_urlsafe(18), actor_id, resource_id, action, preview,
            datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        self._audit.write(make_audit_event("action_proposed", actor_id, resource_id, action))
        return proposal

    def record_approval(
        self, proposal: ActionProposal, confirming_actor_id: str, explicit_confirmation: bool
    ) -> bool:
        approved = (
            explicit_confirmation is True
            and confirming_actor_id == proposal.actor_id
            and datetime.now(timezone.utc) < proposal.expires_at
            and proposal.action in ALLOWED_ACTIONS
        )
        result = "approved_for_review_only" if approved else "rejected_or_expired"
        self._audit.write(
            make_audit_event("action_approval", confirming_actor_id, proposal.resource_id, result)
        )
        return approved
