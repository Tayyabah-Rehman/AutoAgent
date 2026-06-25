"""
AutoAgent Database Layer — SQLite
Handles: users, sessions, chat threads, messages, query history, uploaded files
"""
import sqlite3
import hashlib
import hmac
import secrets
import os
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "autoagent.db")


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables on first run."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt        TEXT NOT NULL,
            role        TEXT DEFAULT 'user',
            created_at  TEXT DEFAULT (datetime('now')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            expires_at  TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        -- Chat threads (conversations)
        CREATE TABLE IF NOT EXISTS chat_threads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT DEFAULT 'New Chat',
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        -- Messages within chat threads
        CREATE TABLE IF NOT EXISTS chat_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id   INTEGER NOT NULL,
            role        TEXT NOT NULL,  -- 'user' or 'assistant'
            content     TEXT NOT NULL,
            tool_count  INTEGER DEFAULT 0,
            duration    REAL DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
        );

        -- Legacy query history (kept for backward compatibility)
        CREATE TABLE IF NOT EXISTS query_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            query       TEXT NOT NULL,
            answer      TEXT,
            steps_json  TEXT,
            tool_count  INTEGER DEFAULT 0,
            duration    REAL DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS uploaded_files (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            filename    TEXT NOT NULL,
            file_path   TEXT NOT NULL,
            file_size   INTEGER,
            file_type   TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)


# ── Password Hashing ──────────────────────────────────────

def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000)
    return key.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000)
    return hmac.compare_digest(key.hex(), stored_hash)


# ── User Management ───────────────────────────────────────

def create_user(username: str, email: str, password: str, role: str = "user") -> tuple[bool, str]:
    try:
        pwd_hash, salt = hash_password(password)
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, salt, role) VALUES (?,?,?,?,?)",
                (username.strip().lower(), email.strip().lower(), pwd_hash, salt, role)
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "Email already registered."
        return False, "Registration failed."


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username.strip().lower(),)
        ).fetchone()
    if not row:
        return None
    if not verify_password(password, row["password_hash"], row["salt"]):
        return None
    # Update last login
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (row["id"],))
    return dict(row)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def list_users() -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id,username,email,role,created_at,last_login FROM users ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def delete_user(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))


# ── Session Management ────────────────────────────────────

def create_session(user_id: int, hours: int = 24 * 30) -> str:  # 30-day sessions for persistent login
    token = secrets.token_urlsafe(48)
    expires = f"datetime('now', '+{hours} hours')"
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, {expires})",
            (token, user_id)
        )
    return token


def validate_session(token: str) -> Optional[Dict]:
    if not token:
        return None
    with get_conn() as conn:
        row = conn.execute(
            """SELECT u.* FROM sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.token=? AND s.expires_at > datetime('now')""",
            (token,)
        ).fetchone()
    return dict(row) if row else None


def destroy_session(token: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))


def cleanup_expired_sessions():
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at <= datetime('now')")


# ── Chat Threads ──────────────────────────────────────────

def create_chat_thread(user_id: int, title: str = "New Chat") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO chat_threads (user_id, title) VALUES (?, ?)",
            (user_id, title)
        )
        return cur.lastrowid


def get_user_threads(user_id: int, limit: int = 100) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT t.*, COUNT(m.id) as message_count 
               FROM chat_threads t
               LEFT JOIN chat_messages m ON m.thread_id = t.id
               WHERE t.user_id=?
               GROUP BY t.id
               ORDER BY t.updated_at DESC
               LIMIT ?""",
            (user_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def get_thread(thread_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM chat_threads WHERE id=?", (thread_id,)).fetchone()
    return dict(row) if row else None


def update_thread_title(thread_id: int, title: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE chat_threads SET title=?, updated_at=datetime('now') WHERE id=?",
            (title, thread_id)
        )


def delete_thread(thread_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM chat_threads WHERE id=? AND user_id=?", (thread_id, user_id))


def update_thread_timestamp(thread_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE chat_threads SET updated_at=datetime('now') WHERE id=?",
            (thread_id,)
        )


# ── Chat Messages ─────────────────────────────────────────

def add_chat_message(thread_id: int, role: str, content: str, tool_count: int = 0, duration: float = 0) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO chat_messages (thread_id, role, content, tool_count, duration) VALUES (?, ?, ?, ?, ?)",
            (thread_id, role, content, tool_count, duration)
        )
        # Update thread timestamp
        conn.execute("UPDATE chat_threads SET updated_at=datetime('now') WHERE id=?", (thread_id,))
        return cur.lastrowid


def get_thread_messages(thread_id: int) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE thread_id=? ORDER BY created_at ASC",
            (thread_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_thread_messages(thread_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM chat_messages WHERE thread_id=?", (thread_id,))


# ── Legacy Query History ──────────────────────────────────

def save_query(user_id: int, query: str, answer: str, steps_json: str, tool_count: int, duration: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO query_history (user_id,query,answer,steps_json,tool_count,duration) VALUES (?,?,?,?,?,?)",
            (user_id, query, answer, steps_json, tool_count, duration)
        )


def get_user_history(user_id: int, limit: int = 50) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM query_history WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_history(limit: int = 200) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT qh.*, u.username FROM query_history qh
               JOIN users u ON u.id=qh.user_id
               ORDER BY qh.created_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_history_item(item_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM query_history WHERE id=? AND user_id=?", (item_id, user_id))


# ── File Records ──────────────────────────────────────────

def save_file_record(user_id: int, filename: str, file_path: str, file_size: int, file_type: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO uploaded_files (user_id,filename,file_path,file_size,file_type) VALUES (?,?,?,?,?)",
            (user_id, filename, file_path, file_size, file_type)
        )
        return cur.lastrowid


def get_user_files(user_id: int) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM uploaded_files WHERE user_id=? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_file_record(file_id: int, user_id: int) -> Optional[str]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT file_path FROM uploaded_files WHERE id=? AND user_id=?", (file_id, user_id)
        ).fetchone()
        if row:
            conn.execute("DELETE FROM uploaded_files WHERE id=?", (file_id,))
            return row["file_path"]
    return None


# ── Stats ─────────────────────────────────────────────────

def get_stats() -> Dict:
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_queries = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
        total_files = conn.execute("SELECT COUNT(*) FROM uploaded_files").fetchone()[0]
        avg_duration = conn.execute("SELECT AVG(duration) FROM query_history").fetchone()[0] or 0
        total_threads = conn.execute("SELECT COUNT(*) FROM chat_threads").fetchone()[0]
    return {
        "total_users": total_users,
        "total_queries": total_queries,
        "total_files": total_files,
        "avg_duration": round(avg_duration, 2),
        "total_threads": total_threads,
    }