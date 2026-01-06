from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def admin_required(fn):
    """Require JWT with is_admin=True claim."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt() or {}
        if not claims.get('is_admin'):
            return jsonify({'msg': 'Admins only'}), 403
        return fn(*args, **kwargs)

    return wrapper
