"""
Security utilities — API key validation, input sanitization.
"""
import os
import re
import hmac
import hashlib
from typing import Optional


def load_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """
    Load API key safely: prefer env var, fall back to provided key.
    Never logs or exposes the key.
    """
    key = os.environ.get("GROQ_API_KEY") or provided_key
    if not key:
        return None
    return key.strip()


def validate_api_key_format(key: str) -> bool:
    """Basic format check for Groq API keys (gsk_...)."""
    if not key:
        return False
    return bool(re.match(r"^gsk_[A-Za-z0-9]{50,}$", key.strip()))


def mask_key(key: str) -> str:
    """Return masked version for display: gsk_****...xxxx"""
    if not key or len(key) < 10:
        return "****"
    return key[:6] + "****" + key[-4:]


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Basic input sanitization — strip control chars, limit length."""
    if not text:
        return ""
    # Remove null bytes and control characters (except newline/tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:max_length].strip()
