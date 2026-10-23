
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def register_user(username, password):
    username = username.strip()

    if len(username) < 3 or len(username) > 30:
        return False, "Username must be 3–30 characters long."

    if not all(ch.isalnum() or ch in "_-" for ch in username):
        return False, "Use only letters, numbers, underscores, or hyphens."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if len(password) > 128:
        return False, "Password must be no longer than 128 characters."

    password_hash = generate_password_hash(password)

    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
        return True, "Account created successfully! You can now sign in."

    except sqlite3.IntegrityError:
        return False, "That username already exists. Choose another."

    except sqlite3.Error:
        return False, "Unable to save your account. Please try again."


def verify_user(username, password):
    try:
        with get_connection() as connection:
            user = connection.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()

        if user is None:
            return False

        return check_password_hash(user["password_hash"], password)

    except sqlite3.Error:
        return False


init_db()
