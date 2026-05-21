"""
auth_service.py — Session management and security
Author: Salma Hani  |  ID: 120210255
"""

import uuid
from functools import wraps
from flask import session, request, jsonify


def require_session(f):
    """
    Decorator: ensures a session exists, creates one if not.
    Validates IP + User-Agent binding on existing sessions.
    Returns 401 if session binding is violated.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
            session["bound_ip"] = request.remote_addr
            session["bound_ua"] = request.headers.get("User-Agent", "")
        else:
            if not validate_session_binding():
                session.clear()
                return jsonify({"error": "Session invalid. Please refresh.", "code": "SESSION_INVALID"}), 401
        return f(*args, **kwargs)
    return decorated


def validate_session_binding() -> bool:
    """
    Returns False if the request IP or User-Agent has changed
    from what was recorded at session creation.
    """
    current_ip = request.remote_addr
    current_ua = request.headers.get("User-Agent", "")
    return (
        session.get("bound_ip") == current_ip and
        session.get("bound_ua") == current_ua
    )
