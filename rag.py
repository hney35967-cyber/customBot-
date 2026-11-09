import os
from pathlib import Path

import numpy as np
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def _get_secret(name: str, default: str | None = None) -> str | None:
    """Read a setting from .env / environment first, then Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return default


API_KEY = _get_secret("GEMINI_API_KEY")
CHAT_MODEL = _get_secret("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
EMBED_MODEL = _get_secret("GEMINI_EMBED_MODEL", "gemini-embedding-001")
