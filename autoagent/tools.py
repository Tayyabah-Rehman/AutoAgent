"""
AutoAgent Tools — Web search, code execution, file reading, Q&A
"""
import os
import subprocess
import tempfile
import traceback
from typing import Optional
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")
        if not results:
            return "No results found for that query."
        return "\n---\n".join(results)
    except Exception as e:
        return f"Search failed: {str(e)}"


def run_python_code(code: str) -> str:
    """Execute Python code safely in a subprocess with timeout."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        os.unlink(tmp_path)

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output.strip() or "Code ran with no output."
    except subprocess.TimeoutExpired:
        return "Code execution timed out (15s limit)."
    except Exception as e:
        return f"Execution error: {str(e)}"


def read_file(filepath: str) -> str:
    """Read a text file and return its contents."""
    try:
        filepath = filepath.strip().strip('"').strip("'")
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        if os.path.getsize(filepath) > 500_000:
            return "File too large (>500KB). Please provide a smaller file."
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return content[:8000] + ("\n\n[Truncated — file is large]" if len(content) > 8000 else "")
    except Exception as e:
        return f"Could not read file: {str(e)}"


def answer_question(question: str) -> str:
    """Placeholder — the LLM itself handles general Q&A."""
    return f"[General Q&A — passed to LLM]: {question}"


TOOL_DESCRIPTIONS = {
    "web_search": {
        "fn": web_search,
        "description": "Search the web for current information. Input: search query string.",
        "example": 'web_search("latest AI research 2024")',
    },
    "run_python": {
        "fn": run_python_code,
        "description": "Run Python code and return the output. Input: valid Python code string.",
        "example": 'run_python("print(2**10)")',
    },
    "read_file": {
        "fn": read_file,
        "description": "Read the contents of a local file. Input: file path string.",
        "example": 'read_file("/path/to/file.txt")',
    },
}
