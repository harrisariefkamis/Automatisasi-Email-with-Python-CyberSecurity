"""Streamlit website prototype with Supabase Auth and a privacy-first workspace.

Gmail OAuth and external AI actions remain disabled until their server-side
consent, callback, and secure token-storage flows are implemented.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# This repository uses a src/ layout. Make the package importable on Streamlit
# Community Cloud even when the project itself has not been installed editable.
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from email_assistant.core import as_jsonable, triage_email  # noqa: E402

st.set_page_config(
    page_title="Email Job Assistant",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1180px; padding-top: 2rem; }
    .hero {
        background: linear-gradient(120deg, #102a43, #176b87);
        color: white; border-radius: 18px; padding: 1.5rem 1.7rem;
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; color: white; }
    .hero p { margin: .45rem 0 0; opacity: .92; }
    div[data-testid="stMetric"] {
        border: 1px solid #e8edf2; border-radius: 12px;
        background: white; padding: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _supabase_client():
    """Create an Auth client from public project settings; never use service role."""
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        anon_key = st.secrets.get("SUPABASE_ANON_KEY", "")
    except Exception:
        return None
    if not url or not anon_key:
        return None
    try:
        from supabase import create_client

        return create_client(url, anon_key)
    except Exception:
        return None


def _auth_page() -> None:
    st.markdown(
        '<div class="hero"><h1>📨 Email Job Assistant</h1>'
        '<p>Tinjau email lowongan dalam workspace yang mengutamakan privasi.</p></div>',
        unsafe_allow_html=True,
    )
    _, center, _ = st.columns([1, 1.15, 1])
    with center:
        st.subheader("Akun website")
        st.caption("Login website terpisah dari izin untuk mengakses Gmail.")
        client = _supabase_client()
        if client is None:
            st.info(
                "Untuk mengaktifkan login, atur `SUPABASE_URL` dan `SUPABASE_ANON_KEY` "
                "di Streamlit secrets. Jangan gunakan service-role key."
            )

        mode = st.radio("Pilih", ["Masuk", "Daftar"], horizontal=True)
        with st.form("auth_form"):
            email = st.text_input("Email", autocomplete="email")
            password = st.text_input(
                "Kata sandi", type="password", autocomplete="current-password"
            )
            submitted = st.form_submit_button(
                "Masuk" if mode == "Masuk" else "Buat akun",
                type="primary",
                use_container_width=True,
                disabled=client is None,
            )

        if submitted and client is not None:
            try:
                if mode == "Masuk":
                    result = client.auth.sign_in_with_password(
                        {"email": email.strip(), "password": password}
                    )
                else:
                    result = client.auth.sign_up(
                        {"email": email.strip(), "password": password}
                    )
                user = getattr(result, "user", None)
                session = getattr(result, "session", None)
                if mode == "Daftar" and session is None:
                    st.success("Akun dibuat. Periksa email untuk verifikasi sebelum masuk.")
                elif user is not None and session is not None:
                    st.session_state["user_email"] = user.email or email.strip()
                    st.session_state["supabase_user_id"] = str(user.id)
                    st.session_state["supabase_access_token"] = session.access_token
                    st.session_state["supabase_refresh_token"] = session.refresh_token
                    st.rerun()
                else:
                    st.error("Auth belum menghasilkan sesi. Periksa pengaturan Supabase Auth.")
            except Exception:
                # Avoid exposing auth provider details, passwords, or tokens in the UI.
                st.error("Autentikasi gagal. Periksa kredensial atau konfigurasi Auth.")

        with st.expander("Lupa kata sandi?"):
            reset_email = st.text_input("Email untuk pemulihan", key="reset_email")
            if st.button("Kirim tautan pemulihan", disabled=client is None):
                try:
                    if not reset_email.strip():
                        st.error("Masukkan email akun terlebih dahulu.")
                    else:
                        client.auth.reset_password_for_email(reset_email.strip())
                        st.success("Jika akun tersedia, instruksi pemulihan akan dikirim.")
                except Exception:
                    st.success("Jika akun tersedia, instruksi pemulihan akan dikirim.")

        st.caption(
            "Gmail belum terhubung. Persetujuan Google OAuth akan diminta secara terpisah."
        )


def _workspace() -> None:
    st.markdown(
        '<div class="hero"><h1>Workspace Email</h1>'
        '<p>Triase dan tinjau email. Keputusan dan tindakan tetap di tangan Anda.</p></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Masuk sebagai **{st.session_state.get('user_email', '')}**")
    st.warning(
        "Gmail belum terhubung. Belum ada inbox yang dibaca atau dimodifikasi. "
        "Login website tidak memberikan akses Gmail."
    )

    overview, inbox, jobs, assistant, settings = st.tabs(
        ["Ringkasan", "Kotak Masuk", "Lowongan", "Asisten AI", "Pengaturan"]
    )
    with overview:
        one, two, three = st.columns(3)
        one.metric("Email tersinkron", "—", help="Hubungkan Gmail setelah OAuth tersedia")
        two.metric("Lowongan ditemukan", "—")
        three.metric("Perlu ditinjau", "—")
        st.subheader("Mulai dengan aman")
        st.markdown(
            "1. Hubungkan Gmail dengan OAuth terpisah dan izin baca-saja.\n"
            "2. Pilih email yang ingin dianalisis.\n"
            "3. Setujui pemrosesan AI secara terpisah bila diperlukan."
        )

    with inbox:
        st.subheader("Kotak Masuk")
        st.info("Gmail OAuth belum dikonfigurasi untuk sesi pengguna.")
        st.markdown("#### Hubungkan Gmail")
        st.write(
            "Akses Gmail memerlukan persetujuan Google, terpisah dari login website. "
            "MVP direncanakan hanya membaca email; tidak ada aksi kirim atau hapus."
        )
        st.button("Hubungkan Gmail", type="primary", disabled=True)
        st.caption("Scope yang direncanakan: `gmail.readonly`.")

    with jobs:
        st.subheader("Tinjauan lowongan")
        st.caption("Demo ini menganalisis hanya teks yang Anda masukkan.")
        with st.form("triage_form"):
            sender = st.text_input("Pengirim", key="triage_sender")
            subject = st.text_input("Subjek", key="triage_subject")
            body = st.text_area("Isi email", height=220, key="triage_body")
            analyze = st.form_submit_button("Analisis email", type="primary")
        if analyze:
            result = triage_email({"from": sender, "subject": subject, "body": body})
            st.session_state["last_triage"] = as_jsonable(result)
        if st.session_state.get("last_triage"):
            st.json(st.session_state["last_triage"])

    with assistant:
        st.subheader("Asisten AI")
        st.info(
            "AI eksternal belum diaktifkan dari website. Bila kelak tersedia, konten hanya "
            "dikirim setelah Anda menyetujui pemrosesan untuk email pilihan."
        )
        st.checkbox("Saya setuju mengirim email pilihan ke layanan AI", disabled=True)
        st.text_input("Tanyakan tentang email", disabled=True)
        st.button("Kirim", disabled=True)

    with settings:
        st.subheader("Akun dan privasi")
        st.write(f"Akun website: `{st.session_state.get('user_email', '')}`")
        st.write("Akun Gmail: belum terhubung")
        st.write("Penyimpanan isi email: nonaktif secara default")
        if st.button("Keluar"):
            client = _supabase_client()
            if client is not None:
                try:
                    client.auth.sign_out()
                except Exception:
                    pass
            for key in (
                "user_email",
                "supabase_user_id",
                "supabase_access_token",
                "supabase_refresh_token",
                "last_triage",
            ):
                st.session_state.pop(key, None)
            st.rerun()


if _signed_in := bool(st.session_state.get("user_email")):
    _workspace()
else:
    _auth_page()
