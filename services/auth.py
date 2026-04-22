from functools import wraps

from flask import abort, session


def require_role(expected_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            user_id = session.get("user_id")
            role = session.get("role")
            if not user_id:
                abort(401)
            if expected_role is not None and role != expected_role:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
