from .permisos import rol_de


def rol(request):
    return {"rol": rol_de(request.user) if request.user.is_authenticated else None}
