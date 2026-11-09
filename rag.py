"""
rag.py - Retrieval + answer generation using Google Gemini.

How it works (simple version):
1. Read the FAQ file and split it into small chunks.
2. Turn every chunk into numbers (an "embedding") using Gemini.
3. When a user asks a question, find the chunks most similar to it.
4. Give those chunks + the question to Gemini and ask for a simple,
   friendly, easy-to-understand answer.
"""

import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

DATA_FILE = Path(__file__).parent / "data" / "company_faq.txt"

SYSTEM_PROMPT = """You are a friendly helper who explains things the way a kind, \
patient friend would.

Rules for every answer:
- Use simple everyday words. Avoid jargon; if you must use a technical term, \
explain it in one short phrase.
- Start with a direct answer in the first sentence, then add a little detail.
- Use a short real-life example or analogy when it helps the person understand.
- Keep it short and clear (usually under 150 words).
- Write in plain text only. Do NOT use markdown symbols such as *, #, or backticks. \
If you need a list, use simple lines starting with "- ".
- Use the COMPANY INFORMATION below as your main source. If it does not contain \
the answer, you may explain the concept using general knowledge, but say clearly \
that this is general information and not from the company's records.
- Never invent company-specific facts (prices, policies, phone numbers)."""


def _get_client() -> genai.Client:
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Copy .env.example to .env and add your key."
        )
    return genai.Client(api_key=API_KEY)


def load_chunks(path: Path = DATA_FILE) -> list[str]:
    """Split the FAQ file into chunks (one Q&A block per chunk)."""
    text = path.read_text(encoding="utf-8")
    chunks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return chunks


class KnowledgeBase:
    def __init__(self, path: Path = DATA_FILE):
        self.client = _get_client()
        self.chunks = load_chunks(path)
        self.vectors = self._embed(self.chunks, task_type="RETRIEVAL_DOCUMENT")

    def _embed(self, texts: list[str], task_type: str) -> np.ndarray:
        vectors = []
        for i in range(0, len(texts), 50):  # send in small batches
            resp = self.client.models.embed_content(
                model=EMBED_MODEL,
                contents=texts[i : i + 50],
                config=types.EmbedContentConfig(task_type=task_type),
            )
            vectors.extend(e.values for e in resp.embeddings)
        arr = np.array(vectors, dtype=np.float32)
        arr /= np.linalg.norm(arr, axis=1, keepdims=True)  # normalise for cosine
        return arr

    def search(self, question: str, top_k: int = 3) -> list[str]:
        q_vec = self._embed([question], task_type="RETRIEVAL_QUERY")[0]
        scores = self.vectors @ q_vec
        best = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in best]

    def answer(self, question: str, history: list[dict] | None = None) -> str:
        context = "\n\n".join(self.search(question))

        # Include the last few messages so follow-up questions make sense
        convo = ""
        for msg in (history or [])[-6:]:
            who = "User" if msg["role"] == "user" else "Assistant"
            convo += f"{who}: {msg['content']}\n"

        prompt = (
            f"COMPANY INFORMATION:\n{context}\n\n"
            f"CONVERSATION SO FAR:\n{convo or '(none)'}\n"
            f"USER QUESTION: {question}\n\n"
            "Answer in a simple, friendly, easy-to-understand way."
        )

        resp = self.client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
            ),
        )
        return (resp.text or "Sorry, I couldn't come up with an answer. Please try again.").strip()
