"""Validated environment configuration for optional integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Invalid or incomplete non-secret configuration."""


@dataclass(frozen=True)
class Settings:
    app_env: str
    max_email_chars: int
    google_client_id: str
    google_client_secret: str
    openai_api_key: str
    openai_model: str
    supabase_url: str
    supabase_anon_key: str
    api_access_token: str
    persist_email_body: bool

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        app_env = source.get("APP_ENV", "development").strip().lower()
        if app_env not in {"development", "test", "production"}:
            raise ConfigurationError("APP_ENV must be development, test, or production")
        try:
            max_chars = int(source.get("MAX_EMAIL_CHARS", "20000"))
        except ValueError as exc:
            raise ConfigurationError("MAX_EMAIL_CHARS must be an integer") from exc
        if not 1000 <= max_chars <= 100000:
            raise ConfigurationError("MAX_EMAIL_CHARS must be between 1000 and 100000")
        persist = source.get("PERSIST_EMAIL_BODY", "false").strip().lower()
        if persist not in {"true", "false"}:
            raise ConfigurationError("PERSIST_EMAIL_BODY must be true or false")
        return cls(
            app_env=app_env,
            max_email_chars=max_chars,
            google_client_id=source.get("GOOGLE_CLIENT_ID", "").strip(),
            google_client_secret=source.get("GOOGLE_CLIENT_SECRET", "").strip(),
            openai_api_key=source.get("OPENAI_API_KEY", "").strip(),
            openai_model=source.get("OPENAI_MODEL", "gpt-4o-mini").strip(),
            supabase_url=source.get("SUPABASE_URL", "").strip().rstrip("/"),
            supabase_anon_key=source.get("SUPABASE_ANON_KEY", "").strip(),
            api_access_token=source.get("API_ACCESS_TOKEN", "").strip(),
            persist_email_body=persist == "true",
        )

    def require(self, *names: str) -> None:
        missing = [name for name in names if not getattr(self, name)]
        if missing:
            raise ConfigurationError("Missing required configuration: " + ", ".join(missing))
