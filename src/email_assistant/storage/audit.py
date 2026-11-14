"""Metadata-only audit records; production should use protected append-only storage."""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Protocol

logger = logging.getLogger("email_assistant.audit")


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    actor_id: str
    resource_id: str
    outcome: str
    timestamp: str


class AuditSink(Protocol):
    def write(self, event: AuditEvent) -> None: ...


class LoggingAuditSink:
    def write(self, event: AuditEvent) -> None:
        logger.info("audit_event=%s", json.dumps(asdict(event), separators=(",", ":")))


def make_audit_event(event_type: str, actor_id: str, resource_id: str, outcome: str) -> AuditEvent:
    return AuditEvent(
        event_type=event_type[:64],
        actor_id=actor_id[:128],
        resource_id=resource_id[:256],
        outcome=outcome[:64],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
