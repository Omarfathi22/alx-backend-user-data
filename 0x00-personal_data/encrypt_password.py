#!/usr/bin/env python3
"""A module for encrypting and verifying passwords."""

import bcrypt # type: ignore

def hash_password(password: str) -> bytes:
    """Hashes a password with a randomly generated salt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def is_valid(hashed_password: bytes, password: str) -> bool:
    """Verifies if a password matches its hashed version."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
