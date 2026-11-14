"""Rule-based email triage demo. Does not connect to or modify an email account."""

import re
from dataclasses import asdict, dataclass
from typing import Any

JOB_TERMS = (
    "job opening", "job opportunity", "career opportunity", "vacancy",
    "we are hiring", "recruitment", "lowongan", "lamaran", "rekrutmen",
    "wawancara", "interview",
)
SPAM_TERMS = ("claim your prize", "guaranteed income", "verify your password")
SUBSCRIPTION_TERMS = ("unsubscribe", "berhenti berlangganan", "manage preferences")


@dataclass(frozen=True)
class TriageResult:
    category: str
    confidence: float
    labels: list[str]
    reasons: list[str]
    unsubscribe_detected: bool
    cleanup_candidate: bool
    job_analysis: dict[str, Any] | None = None


def analyze_job(text: str) -> dict[str, Any]:
    """Return basic review hints; this is not an AI verdict or job verification."""
    terms = [term for term in JOB_TERMS if term in text.lower()]
    url = re.search(r"https?://[^\s<>\"']+", text)
    return {
        "matched_terms": terms,
        "application_url": url.group(0).rstrip(".,);]") if url else None,
        "review_note": "Periksa perusahaan, tautan, kualifikasi, dan tenggat secara manual.",
    }


def triage_email(email: dict[str, Any]) -> TriageResult:
    text = " ".join(
        str(email.get(key, ""))
        for key in ("from", "subject", "body")
    )
    lowered = text.lower()
    jobs = [term for term in JOB_TERMS if term in lowered]
    spam = [term for term in SPAM_TERMS if term in lowered]
    headers = email.get("headers", {})
    list_unsubscribe = bool(
        headers.get("List-Unsubscribe") or headers.get("list-unsubscribe")
    )
    unsub = list_unsubscribe or any(term in lowered for term in SUBSCRIPTION_TERMS)

    if spam:
        category, confidence, reasons = "spam_review", 0.75, [f"Sinyal spam: {spam[0]}"]
        labels = ["Spam-Review"]
    elif jobs:
        category, confidence, reasons = "job", 0.80, [f"Sinyal lowongan: {jobs[0]}"]
        labels = ["Lowongan/Review"]
    elif unsub:
        category, confidence, reasons = "subscription_review", 0.70, ["Sinyal langganan ditemukan"]
        labels = ["Langganan/Review"]
    else:
        category, confidence, reasons = "general_review", 0.50, ["Perlu pemeriksaan manual"]
        labels = ["Perlu Ditinjau"]

    # Ini hanya rekomendasi review. Tidak ada unsubscribe atau penghapusan otomatis.
    cleanup_candidate = category == "subscription_review" and not jobs
    return TriageResult(
        category=category,
        confidence=confidence,
        labels=labels,
        reasons=reasons,
        unsubscribe_detected=unsub,
        cleanup_candidate=cleanup_candidate,
        job_analysis=analyze_job(text) if jobs else None,
    )


def as_jsonable(result: TriageResult) -> dict[str, Any]:
    return asdict(result)
