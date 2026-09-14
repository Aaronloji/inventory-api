from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_smorest import abort


def roles_required(*roles):
    """Exige un JWT válido cuyo claim `role` esté dentro de `roles`.

    Uso:
        @roles_required(Role.ADMIN, Role.MANAGER)
        def post(self, data): ...
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                abort(403, message="No tiene permisos para esta operación.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
