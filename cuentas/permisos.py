from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Rol


def rol_de(usuario) -> str:
    if usuario.is_superuser:
        return Rol.ADMIN
    perfil = getattr(usuario, "perfil", None)
    return perfil.rol if perfil else Rol.ESTUDIANTE


def rol_requerido(*roles):
    """Exige sesión y uno de los roles; si no, responde 403 (verificado en el servidor)."""
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if rol_de(request.user) not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador
