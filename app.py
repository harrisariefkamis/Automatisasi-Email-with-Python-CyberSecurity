"""Streamlit demo. Only analyzes text entered by the user; no mailbox access."""

import streamlit as st

from email_assistant.chat import answer_question
from email_assistant.core import as_jsonable, triage_email

st.set_page_config(page_title="Email Job Assistant", page_icon="📨")
st.title("Asisten Email Lowongan — Demo Lokal")
st.warning(
    "Demo ini tidak terhubung ke akun email. Tidak ada email yang dikirim, "
    "dihapus, diblokir, atau di-unsubscribe."
)

with st.form("email_form"):
    sender = st.text_input("Pengirim")
    subject = st.text_input("Subjek")
    body = st.text_area("Isi email")
    submitted = st.form_submit_button("Analisis email")

if submitted:
    result = triage_email({"from": sender, "subject": subject, "body": body})
    st.subheader("Hasil triase")
    st.json(as_jsonable(result))
    if result.job_analysis:
        st.subheader("Petunjuk analisis lowongan")
        st.json(result.job_analysis)

st.subheader("Chatbox demo")
st.caption("Jawaban masih berbasis aturan lokal, bukan model AI.")
if "chat" not in st.session_state:
    st.session_state.chat = []

for item in st.session_state.chat:
    with st.chat_message(item["role"]):
        st.write(item["content"])

question = st.chat_input("Tanyakan tentang email atau lowongan")
if question:
    st.session_state.chat.append({"role": "user", "content": question})
    response = answer_question(question, body if "body" in locals() else "")
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.rerun()
