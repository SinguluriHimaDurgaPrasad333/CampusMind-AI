"""
CampusAI - Admin Authentication Module
======================================
Provides simple, beginner-friendly password-based authentication
for administrative functions (document upload, re-indexing, deletion).
Designed for college project demonstration and viva presentation.
"""

import hashlib
import streamlit as st
from config import ADMIN_PASSWORD_HASH


def hash_password(password: str) -> str:
    """Computes SHA-256 hash of a plaintext password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str) -> bool:
    """Verifies user input against configured admin password hash."""
    if not plain_password:
        return False
    entered_hash = hash_password(plain_password.strip())
    return entered_hash == ADMIN_PASSWORD_HASH.strip()


def is_admin_authenticated() -> bool:
    """Checks whether administrator session is currently active in Streamlit."""
    return st.session_state.get("admin_authenticated", False)


def login_admin(password: str) -> bool:
    """Validates password and sets session authentication state."""
    if verify_password(password):
        st.session_state["admin_authenticated"] = True
        return True
    return False


def logout_admin() -> None:
    """Clears the admin authentication session state."""
    st.session_state["admin_authenticated"] = False
