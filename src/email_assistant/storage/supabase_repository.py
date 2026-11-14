"""Supabase REST persistence using the end-user JWT so RLS remains active."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from email_assistant.models.email import EmailMessage


class SupabaseStorageError(RuntimeError):
    """Safe storage error without remote response bodies."""


class SupabaseEmailRepository:
    """Stores only with explicit consent and a user's Supabase access token.

    Never pass a service-role key here. Supabase RLS must enforce auth.uid() ownership.
    """

    def __init__(self, url: str, anon_key: str, user_access_token: str, timeout: float = 8.0):
        if not url.startswith("https://") or not anon_key or not user_access_token:
            raise ValueError("HTTPS Supabase URL, anon key, and authenticated user token required")
        self._url = url.rstrip("/")
        self._anon_key = anon_key
        self._user_token = user_access_token
        self._timeout = timeout

    def save_email(
        self,
        user_id: str,
        email: EmailMessage,
        *,
        persistence_consent: bool,
        store_body: bool = False,
    ) -> dict[str, Any]:
        if persistence_consent is not True:
            raise PermissionError("Explicit consent is required to persist email data")
        if not user_id or len(user_id) > 128:
            raise ValueError("A valid authenticated user id is required")
        record = {
            "user_id": user_id,
            "provider": "gmail",
            "provider_message_id": email.provider_id,
            "thread_id": email.thread_id,
            "sender": email.sender,
            "subject": email.subject,
            "body_text": email.body_text if store_body else None,
            "received_at": email.received_at or None,
            "headers": email.headers,
        }
        headers = {
            "apikey": self._anon_key,
            "Authorization": f"Bearer {self._user_token}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        try:
            response = httpx.post(
                f"{self._url}/rest/v1/emails?on_conflict=user_id,provider,provider_message_id",
                headers=headers,
                json=record,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list) or not data:
                raise SupabaseStorageError("Storage returned no row")
            return data[0]
        except SupabaseStorageError:
            raise
        except Exception as exc:
            raise SupabaseStorageError("Email persistence failed") from exc

    def list_email_metadata(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        if not user_id or len(user_id) > 128:
            raise ValueError("A valid authenticated user id is required")
        count = max(1, min(int(limit), 50))
        query = (
            f"user_id=eq.{quote(user_id)}&select=id,provider_message_id,thread_id,sender,"
            f"subject,received_at,created_at&order=created_at.desc&limit={count}"
        )
        headers = {
            "apikey": self._anon_key,
            "Authorization": f"Bearer {self._user_token}",
        }
        try:
            response = httpx.get(
                f"{self._url}/rest/v1/emails?{query}", headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                raise SupabaseStorageError("Storage returned invalid data")
            return data
        except SupabaseStorageError:
            raise
        except Exception as exc:
            raise SupabaseStorageError("Email query failed") from exc
