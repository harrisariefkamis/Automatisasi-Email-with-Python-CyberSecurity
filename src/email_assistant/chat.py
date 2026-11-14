"""Local demo chat responses; not connected to an external AI service."""


def answer_question(question: str, email_text: str = "") -> str:
    q = question.lower()
    if any(word in q for word in ("lowongan", "job", "pekerjaan")):
        return (
            "Saya dapat membantu meninjau email lowongan yang Anda masukkan. "
            "Versi demo belum membaca inbox atau memakai model AI."
        )
    if any(word in q for word in ("hapus", "delete", "unsubscribe", "berhenti")):
        return (
            "Saya tidak melakukan unsubscribe atau menghapus email. "
            "Tinjau dan setujui tindakan semacam itu secara manual."
        )
    if email_text:
        return "Email tersedia untuk ditinjau. Verifikasi pengirim, tautan, dan klaim secara manual."
    return "Masukkan email contoh atau pertanyaan tentang lowongan untuk memulai demo."
