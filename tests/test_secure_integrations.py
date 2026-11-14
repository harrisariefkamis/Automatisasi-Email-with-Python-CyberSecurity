import base64
import unittest
from unittest.mock import patch

from email_assistant.config import ConfigurationError, Settings
from email_assistant.integrations.ai_client import OpenAIJobAssistant
from email_assistant.integrations.gmail_client import (
    GMAIL_READONLY_SCOPE,
    GmailIntegrationError,
    GmailReadOnlyClient,
    normalize_gmail_message,
)
from email_assistant.models.email import EmailMessage
from email_assistant.services.approval_service import ApprovalService
from email_assistant.services.email_triage_service import triage_message
from email_assistant.storage.audit import AuditEvent
from email_assistant.storage.supabase_repository import SupabaseEmailRepository


class FakeCredentials:
    def __init__(self, scopes):
        self.scopes = scopes

    def has_scopes(self, requested):
        return set(requested).issubset(self.scopes)


class MemoryAudit:
    def __init__(self):
        self.events = []

    def write(self, event: AuditEvent):
        self.events.append(event)


class SecureIntegrationTests(unittest.TestCase):
    def test_settings_validate_and_default_body_persistence_off(self):
        settings = Settings.from_env({})
        self.assertFalse(settings.persist_email_body)
        with self.assertRaises(ConfigurationError):
            Settings.from_env({"MAX_EMAIL_CHARS": "10"})

    def test_gmail_rejects_broad_scope_before_network(self):
        with self.assertRaises(GmailIntegrationError):
            GmailReadOnlyClient(FakeCredentials({"https://mail.google.com/"}))

    def test_normalization_limits_fields_and_discards_unknown_headers(self):
        body = base64.urlsafe_b64encode(b"Python job opening").decode().rstrip("=")
        raw = {"id": "m1", "payload": {"mimeType": "text/plain", "headers": [
            {"name": "From", "value": "Recruiter <r@example.com>"},
            {"name": "X-Secret", "value": "discard-me"}], "body": {"data": body}}}
        email = normalize_gmail_message(raw, 1000)
        self.assertEqual(email.sender, "r@example.com")
        self.assertEqual(email.body_text, "Python job opening")
        self.assertEqual(email.headers, {})

    def test_triage_invokes_existing_core(self):
        email = EmailMessage("m", "t", "", "Job opening", "We are hiring", "", {})
        self.assertEqual(triage_message(email).rules_result["category"], "job")

    def test_ai_consent_required_before_call(self):
        email = EmailMessage("m", "t", "", "Job opening", "We are hiring", "", {})
        with self.assertRaises(PermissionError):
            triage_message(email, object(), external_processing_consent=False)
        adapter = object.__new__(OpenAIJobAssistant)
        with self.assertRaises(PermissionError):
            adapter.analyze_job_email("subject", "body", external_processing_consent=False)

    def test_supabase_requires_persistence_consent(self):
        repo = SupabaseEmailRepository("https://example.supabase.co", "anon", "user-jwt")
        email = EmailMessage("m", "t", "", "s", "private", "", {})
        with self.assertRaises(PermissionError):
            repo.save_email("user", email, persistence_consent=False)

    def test_approval_is_actor_bound_and_audited_not_executed(self):
        audit = MemoryAudit()
        approval = ApprovalService(audit)
        proposal = approval.propose("u1", "opaque-message-id", "apply_label", "Preview label")
        self.assertFalse(approval.record_approval(proposal, "u2", True))
        self.assertTrue(approval.record_approval(proposal, "u1", True))
        self.assertEqual(len(audit.events), 3)

    def test_approval_rejects_unallowlisted_action(self):
        with self.assertRaises(ValueError):
            ApprovalService(MemoryAudit()).propose("u", "m", "send", "send email")


if __name__ == "__main__":
    unittest.main()
