"""
app.py - Streamlit chat UI for CustomBot.

Run with:  streamlit run app.py
"""

import io
from datetime import datetime

import streamlit as st
from docx import Document
from fpdf import FPDF

from rag import KnowledgeBase

st.set_page_config(page_title="CustomBot", page_icon="💬", layout="centered")


# ---------- File export helpers ----------
def to_txt(question: str, answer: str) -> bytes:
    return f"Question:\n{question}\n\nAnswer:\n{answer}\n".encode("utf-8")


def to_docx(question: str, answer: str) -> bytes:
    doc = Document()
    doc.add_heading("CustomBot Answer", level=1)
    doc.add_paragraph(datetime.now().strftime("%d %b %Y, %H:%M"))
    doc.add_heading("Question", level=2)
    doc.add_paragraph(question)
    doc.add_heading("Answer", level=2)
    for line in answer.split("\n"):
        doc.add_paragraph(line)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def to_pdf(question: str, answer: str) -> bytes:
    # Built-in PDF fonts only support basic Latin characters, so replace others.
    def clean(text: str) -> str:
        return text.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CustomBot Answer", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, datetime.now().strftime("%d %b %Y, %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Question", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, clean(question), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Answer", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, clean(answer), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def answer_actions(question: str, answer: str, key: str):
    """Show the copy box + download buttons under an answer."""
    with st.expander("📋 Copy or download this answer"):
        st.caption("Use the copy icon at the top-right of the box below:")
        st.code(answer, language=None, wrap_lines=True)

        c1, c2, c3 = st.columns(3)
        c1.download_button(
            "⬇️ Text (.txt)", to_txt(question, answer),
            file_name="answer.txt", mime="text/plain", key=f"txt_{key}",
            use_container_width=True,
        )
        c2.download_button(
            "⬇️ Word (.docx)", to_docx(question, answer),
            file_name="answer.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_{key}", use_container_width=True,
        )
        c3.download_button(
            "⬇️ PDF (.pdf)", to_pdf(question, answer),
            file_name="answer.pdf", mime="application/pdf", key=f"pdf_{key}",
            use_container_width=True,
        )


# ---------- Load knowledge base once ----------
@st.cache_resource(show_spinner="Getting things ready...")
def load_kb() -> KnowledgeBase:
    return KnowledgeBase()


try:
    kb = load_kb()
except Exception as e:
    st.error(f"Setup problem: {e}")
    st.stop()


# ---------- Page ----------
st.title("💬 CustomBot")
st.caption("Ask me anything. I'll explain it in a simple, easy way.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("About")
    st.write("Answers come from the company FAQ, explained in plain, friendly language.")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Show earlier messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            question = st.session_state.messages[i - 1]["content"]
            answer_actions(question, msg["content"], key=str(i))

# New question
if user_q := st.chat_input("Type your question here..."):
    history = list(st.session_state.messages)  # history before this question
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.write(user_q)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = kb.answer(user_q, history)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"
        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        answer_actions(user_q, reply, key=str(len(st.session_state.messages) - 1))
