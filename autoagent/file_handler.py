"""
AutoAgent File Handler — Upload, validate, read, serve files
Supports: txt, md, csv, json, xml, yaml, py, js, html, css, sql, log, pdf
"""
import os
from typing import Optional, Tuple
from datetime import datetime

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml",
    ".py", ".js", ".ts", ".html", ".css", ".sql",
    ".log", ".ini", ".cfg", ".toml",
    ".pdf",
}


def ensure_upload_dir(user_id: int) -> str:
    path = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def validate_file(filename: str, size: int) -> Tuple[bool, str]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    if size > MAX_FILE_SIZE:
        return False, f"File too large ({size // 1024}KB). Max is 10MB."
    return True, ""


def save_uploaded_file(user_id: int, file_bytes: bytes, filename: str) -> Tuple[Optional[str], Optional[str], int]:
    """
    Save raw bytes to disk (call uploaded_file.read() BEFORE passing here).
    Returns (saved_path, error_message, file_size)
    """
    try:
        size = len(file_bytes)
        ok, err = validate_file(filename, size)
        if not ok:
            return None, err, 0

        user_dir = ensure_upload_dir(user_id)

        # Sanitize filename — keep original name readable
        safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ").strip()[:100]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_name = f"{timestamp}_{safe_name}"
        file_path = os.path.join(user_dir, final_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path, None, size
    except Exception as e:
        return None, f"Upload failed: {str(e)}", 0


def extract_pdf_text(file_path: str, max_chars: int = 8000) -> str:
    """Extract text from PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_text.append(f"[Page {i+1}]\n{text.strip()}")
            # Stop early if already large enough
            combined = "\n\n".join(pages_text)
            if len(combined) > max_chars:
                combined = combined[:max_chars] + f"\n\n[Truncated — {len(reader.pages)} pages total, showing first {i+1}]"
                return combined
        result = "\n\n".join(pages_text)
        return result if result.strip() else "[PDF appears to be scanned/image-only — no extractable text found]"
    except ImportError:
        return "[pypdf not installed. Run: pip install pypdf]"
    except Exception as e:
        return f"[PDF read error: {str(e)}]"


def read_file_for_agent(file_path: str, max_chars: int = 8000) -> str:
    """Read a saved file and return text content for the agent."""
    try:
        if not os.path.exists(file_path):
            return "File not found on disk."

        ext = os.path.splitext(file_path)[1].lower()

        # PDF — extract text
        if ext == ".pdf":
            return extract_pdf_text(file_path, max_chars)

        # All other allowed types — read as text
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n[Truncated — file has {len(content)} total characters]"
        return content

    except Exception as e:
        return f"Could not read file: {str(e)}"


def delete_file(file_path: str):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass


def format_file_size(size_bytes: int) -> str:
    if not size_bytes:
        return "0 B"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024} KB"
    else:
        return f"{size_bytes / (1024*1024):.1f} MB"


def get_file_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    icons = {
        ".pdf": "📕", ".csv": "📊", ".json": "🗂",
        ".py": "🐍", ".js": "📜", ".html": "🌐",
        ".txt": "📝", ".md": "📝", ".sql": "🗃",
        ".xml": "📋", ".yaml": "📋", ".yml": "📋",
        ".log": "📃",
    }
    return icons.get(ext, "📄")
