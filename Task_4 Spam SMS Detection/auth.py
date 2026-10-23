import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

from database import (
    create_user,
    get_user_by_username,
    get_user_by_email
)


# -----------------------------
# Password hashing
# -----------------------------

password_hasher = PasswordHasher()


def hash_password(password):
    return password_hasher.hash(password)


def verify_password(password, password_hash):
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


# -----------------------------
# Email validation
# -----------------------------

def is_valid_email(email):
    """
    Validate email format.
    """

    email = email.strip()

    # Basic email format
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False

    # Additional checks
    if ".." in email:
        return False

    local_part, domain = email.rsplit("@", 1)

    if local_part.startswith(".") or local_part.endswith("."):
        return False

    if domain.startswith(".") or domain.endswith("."):
        return False

    if ".." in domain:
        return False

    return True


# -----------------------------
# Username validation
# -----------------------------

def is_valid_username(username):
    username = username.strip()

    if len(username) < 3:
        return False

    if len(username) > 30:
        return False

    pattern = r"^[A-Za-z0-9_]+$"

    return bool(re.fullmatch(pattern, username))


# -----------------------------
# Password validation
# -----------------------------

def validate_password(password):

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    return True, "Password is valid."


def register_user(username, email, password, confirm_password):

    username = username.strip()
    email = email.strip().lower()

    # Username validation
    if not is_valid_username(username):
        return False, "Invalid username. Use 3-30 letters, numbers, or underscore."

    # Email validation
    if not is_valid_email(email):
        return False, "Please enter a valid email address."

    # Password validation
    password_valid, password_message = validate_password(password)

    if not password_valid:
        return False, password_message

    # Confirm password
    if password != confirm_password:
        return False, "Passwords do not match."

    # Check existing username
    if get_user_by_username(username):
        return False, "Username already exists."

    # Check existing email
    if get_user_by_email(email):
        return False, "Email address already exists."

    # Hash password
    password_hash = hash_password(password)

    # Create account
    success, message = create_user(
        username,
        email,
        password_hash
    )

    return success, message
def authenticate_user(username, password):

    username = username.strip()

    user = get_user_by_username(username)

    if not user:
        return False, None

    if verify_password(password, user["password_hash"]):
        return True, user

    return False, None