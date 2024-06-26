"""
BCrypt wrapper module.
"""

import logging

import bcrypt

async def check_password(password: str, stored_hash: str):
    """Check if password matches stored hash."""
    stored_hash = bytes(stored_hash.encode('utf-8'))
    # Check if hash and passwords match.
    try:
        if bcrypt.hashpw(
            password.encode('utf-8'),
            stored_hash
        ) == stored_hash:
            return True

    except Exception as e:
        logging.error("BCRYPT: %s", e)
    return False
