"""Simple credential check — swap for real auth when needed."""
import hashlib
from config import USERS


def authenticate(user_id: str, password: str) -> dict | None:
    user = USERS.get(user_id)
    if user and user["password"] == password:
        return {k: v for k, v in user.items() if k != "password"}
    return None


def hash_token(user_id: str, password: str) -> str:
    """Produce a session token from credentials (deterministic for demo)."""
    raw = f"{user_id}:{password}:coolnest-secret"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def verify_token(user_id: str, token: str) -> dict | None:
    user = USERS.get(user_id)
    if not user:
        return None
    expected = hash_token(user_id, user["password"])
    if token == expected:
        return {k: v for k, v in user.items() if k != "password"}
    return None
